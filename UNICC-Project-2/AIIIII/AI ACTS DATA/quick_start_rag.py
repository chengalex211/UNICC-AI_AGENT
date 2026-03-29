#!/usr/bin/env python3
"""
EU Regulations RAG System - 快速开始版本
支持 EU AI Act + GDPR

使用方法:
    python quick_start_rag.py --setup     # 首次运行，构建向量库
    python quick_start_rag.py --query "你的问题"
    python quick_start_rag.py --interactive  # 交互模式
"""

import os
import argparse
from pathlib import Path
from typing import List, Dict

try:
    from langchain.document_loaders import DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chains import RetrievalQA
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
except ImportError:
    print("❌ 缺少依赖包！请运行:")
    print("   pip install langchain openai chromadb tiktoken")
    exit(1)


class SimpleRAG:
    """简化版RAG系统"""

    def __init__(self, data_dir: str, vectorstore_dir: str = "./vectorstore"):
        self.data_dir = Path(data_dir)
        self.vectorstore_dir = Path(vectorstore_dir)
        self.vectorstore = None
        self.qa_chain = None

        # 检查API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  警告: 未设置 OPENAI_API_KEY")
            print("   请设置: export OPENAI_API_KEY='your-key'")
            print("   或者使用本地模式（参考文档）")
            exit(1)

    def setup(self):
        """初始化设置 - 构建向量库"""
        print("\n" + "="*70)
        print("🚀 EU Regulations RAG System - 初始化")
        print("="*70 + "\n")

        # 1. 加载文档
        print("📚 [1/4] 加载文档...")
        documents = self._load_documents()
        print(f"   ✓ 已加载 {len(documents)} 个文档\n")

        # 2. 切分文档
        print("✂️  [2/4] 切分文档...")
        chunks = self._split_documents(documents)
        print(f"   ✓ 已生成 {len(chunks)} 个文本块\n")

        # 3. 创建向量库
        print("🔢 [3/4] 创建向量库（这可能需要几分钟）...")
        self._create_vectorstore(chunks)
        print(f"   ✓ 向量库已保存到: {self.vectorstore_dir}\n")

        # 4. 测试查询
        print("🔍 [4/4] 测试系统...")
        self._load_vectorstore()
        self._setup_qa_chain()

        test_result = self.query("What is the EU AI Act?")
        print("   ✓ 系统测试成功！\n")

        print("="*70)
        print("✅ 设置完成！现在可以开始查询了")
        print("="*70)
        print("\n运行查询:")
        print("  python quick_start_rag.py --query '你的问题'")
        print("\n或启动交互模式:")
        print("  python quick_start_rag.py --interactive\n")

    def _load_documents(self) -> List:
        """加载文档"""
        all_docs = []

        # 加载 EU AI Act
        ai_act_dir = self.data_dir / "Markdown_for_RAG"
        if ai_act_dir.exists():
            loader = DirectoryLoader(
                str(ai_act_dir),
                glob="*.md",
                show_progress=True
            )
            docs = loader.load()

            # 添加元数据
            for doc in docs:
                doc.metadata["regulation"] = "EU AI Act"
                doc.metadata["year"] = "2024"

            all_docs.extend(docs)
            print(f"   • EU AI Act: {len(docs)} 文件")

        # 加载 GDPR
        gdpr_dir = self.data_dir / "GDPR_Markdown"
        if gdpr_dir.exists():
            loader = DirectoryLoader(
                str(gdpr_dir),
                glob="*.md",
                show_progress=True
            )
            docs = loader.load()

            for doc in docs:
                doc.metadata["regulation"] = "GDPR"
                doc.metadata["year"] = "2016"

            all_docs.extend(docs)
            print(f"   • GDPR: {len(docs)} 文件")

        if not all_docs:
            raise ValueError(f"未找到文档！请检查路径: {self.data_dir}")

        return all_docs

    def _split_documents(self, documents: List) -> List:
        """切分文档"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n### Article", "\n### ", "\n## ", "\n\n", "\n", " "]
        )

        return splitter.split_documents(documents)

    def _create_vectorstore(self, chunks: List):
        """创建向量库"""
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(self.vectorstore_dir)
        )

    def _load_vectorstore(self):
        """加载已有向量库"""
        if not self.vectorstore_dir.exists():
            raise ValueError(f"向量库不存在: {self.vectorstore_dir}\n请先运行 --setup")

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = Chroma(
            persist_directory=str(self.vectorstore_dir),
            embedding_function=embeddings
        )

    def _setup_qa_chain(self):
        """设置QA链"""
        if not self.vectorstore:
            self._load_vectorstore()

        # 设置检索器
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

        # 设置LLM
        llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0
        )

        # 自定义Prompt
        template = """你是一位精通欧盟法规的法律助手，专门研究 EU AI Act 和 GDPR。

请仅根据以下上下文回答问题，并引用具体的条款（Article）。

上下文：
{context}

问题：{question}

请按以下格式回答：

**回答：**
[详细回答]

**法律依据：**
- [法规名称] Article X: [简要说明]

**注意事项：**
[如适用]

如果无法根据上下文回答，请明确说明。

回答："""

        PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

    def query(self, question: str) -> Dict:
        """查询"""
        if not self.qa_chain:
            self._setup_qa_chain()

        result = self.qa_chain({"query": question})

        return {
            "question": question,
            "answer": result["result"],
            "sources": result["source_documents"]
        }

    def interactive_mode(self):
        """交互模式"""
        print("\n" + "="*70)
        print("💬 EU Regulations RAG - 交互模式")
        print("="*70)
        print("\n提示:")
        print("  - 输入你的问题按回车")
        print("  - 输入 'quit' 或 'exit' 退出")
        print("  - 输入 'examples' 查看示例问题")
        print("\n" + "-"*70 + "\n")

        # 初始化
        if not self.qa_chain:
            print("正在初始化系统...")
            self._load_vectorstore()
            self._setup_qa_chain()
            print("✅ 系统就绪！\n")

        while True:
            try:
                question = input("❓ 你的问题: ").strip()

                if not question:
                    continue

                if question.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 再见！")
                    break

                if question.lower() == 'examples':
                    self._show_examples()
                    continue

                # 执行查询
                print("\n🔍 正在搜索...")
                result = self.query(question)

                # 显示结果
                print("\n" + "="*70)
                print("💡 回答:")
                print("="*70)
                print(result["answer"])

                # 显示来源
                print("\n" + "-"*70)
                print("📚 来源文档:")
                for i, doc in enumerate(result["sources"][:3], 1):
                    regulation = doc.metadata.get("regulation", "Unknown")
                    print(f"\n{i}. [{regulation}]")
                    print(f"   {doc.page_content[:200]}...")

                print("\n" + "="*70 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}\n")

    def _show_examples(self):
        """显示示例问题"""
        print("\n" + "="*70)
        print("📝 示例问题")
        print("="*70)

        examples = {
            "EU AI Act": [
                "What are high-risk AI systems?",
                "What AI practices are prohibited?",
                "What is a general-purpose AI model?",
                "What are the transparency obligations?"
            ],
            "GDPR": [
                "What are the GDPR principles?",
                "What rights do data subjects have?",
                "What is the role of a Data Protection Officer?",
                "What are the penalties for non-compliance?"
            ],
            "交叉问题": [
                "How does GDPR apply to AI systems?",
                "What data protection requirements apply to high-risk AI?"
            ]
        }

        for category, questions in examples.items():
            print(f"\n{category}:")
            for q in questions:
                print(f"  • {q}")

        print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="EU Regulations RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 首次设置
  python quick_start_rag.py --setup

  # 单次查询
  python quick_start_rag.py --query "What are high-risk AI systems?"

  # 交互模式
  python quick_start_rag.py --interactive

  # 使用自定义数据目录
  python quick_start_rag.py --data-dir "./my_data" --setup
        """
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="首次运行：构建向量库"
    )

    parser.add_argument(
        "--query",
        type=str,
        help="执行单次查询"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="启动交互模式"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default=".",
        help="数据目录路径（默认: 当前目录）"
    )

    parser.add_argument(
        "--vectorstore-dir",
        type=str,
        default="./vectorstore",
        help="向量库保存路径（默认: ./vectorstore）"
    )

    args = parser.parse_args()

    # 创建RAG实例
    rag = SimpleRAG(
        data_dir=args.data_dir,
        vectorstore_dir=args.vectorstore_dir
    )

    # 执行操作
    if args.setup:
        rag.setup()

    elif args.query:
        print("\n🔍 查询中...\n")
        result = rag.query(args.query)

        print("="*70)
        print(f"❓ 问题: {result['question']}")
        print("="*70)
        print(f"\n{result['answer']}\n")
        print("="*70)

    elif args.interactive:
        rag.interactive_mode()

    else:
        parser.print_help()
        print("\n💡 提示: 首次使用请运行 --setup 构建向量库")


if __name__ == "__main__":
    main()
