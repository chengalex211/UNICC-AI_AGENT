# EU AI Act - Markdown文档集合（RAG就绪）

## 📚 文档概述

本目录包含EU AI Act (Regulation 2024/1689)的完整Markdown版本，已优化用于RAG（检索增强生成）系统。

**总文档数:** 8个Markdown文件
**总内容量:** 约500KB纯文本
**覆盖范围:** 完整的EU AI Act法规

---

## 📂 文件结构

### P0 优先级（核心文档）

#### 1. `EU_AI_Act_Chapter_III_Articles_6-51.md` (119.9 KB)
**标题:** Chapter III - High-Risk AI Systems (Articles 6-51)
**内容:** 高风险AI系统的完整规定
**关键主题:**
- 高风险AI系统的分类规则
- 数据治理和质量要求
- 技术文档和记录保存
- 透明度和信息提供
- 人工监督要求
- 准确性、鲁棒性和网络安全

**适用场景:** 判断AI系统是否为高风险、合规要求查询

#### 2. `EU_AI_Act_Annex_III_High-Risk_List.md` (11.7 KB)
**标题:** Annex III - High-Risk AI Systems List
**内容:** 8大类高风险AI系统详细清单
**关键主题:**
- 生物识别和分类
- 关键基础设施管理
- 教育和职业培训
- 就业和工人管理
- 基本服务访问
- 执法
- 移民和边境控制
- 司法和民主进程

**适用场景:** 快速判断特定AI应用是否属于高风险类别

#### 3. `EU_AI_Act_Article_52_Transparency.md` (18.5 KB)
**标题:** Article 52 - Transparency Obligations
**内容:** AI系统透明度要求
**关键主题:**
- AI生成内容的披露义务
- Deepfake标注要求
- 情感识别系统通知
- 生物特征分类系统披露

**适用场景:** 了解AI系统的透明度合规要求

---

### P1 优先级（重要补充）

#### 4. `EU_AI_Act_Chapter_II_Article_5_Prohibited.md` (13.0 KB)
**标题:** Chapter II - Prohibited AI Practices (Article 5)
**内容:** 明确禁止的AI应用
**关键主题:**
- 社会信用评分系统
- 操纵性AI技术
- 利用弱势群体的AI
- 未授权的生物特征分类
- 实时远程生物识别（公共场所）

**适用场景:** 确保AI应用不违反禁止性规定

#### 5. `EU_AI_Act_Chapter_V_Articles_51-55_GPAI.md` (51.0 KB)
**标题:** Chapter V - General-Purpose AI Models (Articles 51-55)
**内容:** 通用AI模型（如GPT、Claude等）专门规定
**关键主题:**
- GPAI模型定义和范围
- 系统性风险评估
- 透明度和文档要求
- 版权和训练数据披露
- 高影响GPAI模型的额外义务

**适用场景:** 大语言模型、基础模型的合规要求

#### 6. `EU_AI_Act_Annex_IV_Technical_Documentation.md` (16.4 KB)
**标题:** Annex IV - Technical Documentation Requirements
**内容:** 技术文档必备内容清单
**关键主题:**
- 系统架构说明
- 数据集描述（训练、验证、测试）
- 性能指标和评估方法
- 风险管理措施
- 质量管理体系

**适用场景:** 准备技术文档、合规审查

---

### P2 优先级（背景知识）

#### 7. `EU_AI_Act_Recitals_1-182.md` (262.2 KB)
**标题:** Recitals (1-182) - Legislative Background
**内容:** 完整的立法序言和背景说明
**关键主题:**
- 法规制定的背景和目标
- 各条款的解释性说明
- 与现有法规的关系
- 风险分类的理由
- 创新与监管的平衡

**适用场景:** 深入理解法规背景、条款解释

#### 8. `EU_AI_Act_Chapter_I_Articles_1-4_General.md` (7.8 KB)
**标题:** Chapter I - General Provisions (Articles 1-4)
**内容:** 一般条款和核心定义
**关键主题:**
- 法规适用范围
- 地域效力（域外管辖）
- 核心术语定义（AI系统、提供者、部署者等）
- 修订程序

**适用场景:** 理解基本概念和适用范围

---

## 🔍 RAG系统使用建议

### 文档切分策略

**推荐chunk大小:** 512-1024 tokens
**推荐overlap:** 50-100 tokens

**切分单位建议:**
1. **按条款切分** - 每个Article作为一个chunk（最精确）
2. **按段落切分** - 保持语义完整性
3. **按页面切分** - 已包含`## Page N`标记

### 元数据建议

为每个chunk添加以下元数据：

```json
{
  "document": "EU_AI_Act_Chapter_III_Articles_6-51.md",
  "title": "Chapter III - High-Risk AI Systems",
  "article": "Article 12",  // 如果适用
  "page": 5,
  "category": "high-risk-systems",
  "priority": "P0",
  "regulation": "EU 2024/1689",
  "date": "2024-06-13"
}
```

### 向量化建议

**推荐Embedding模型:**
- OpenAI: `text-embedding-3-large` (1024维)
- Sentence Transformers: `all-MiniLM-L6-v2`
- 中文支持: `paraphrase-multilingual-MiniLM-L12-v2`

**向量数据库选项:**
- Pinecone (云端)
- Weaviate (开源)
- Qdrant (开源)
- ChromaDB (轻量级)

### 查询优化

**关键词索引:**
- "high-risk AI" → Chapter III, Annex III
- "prohibited" → Chapter II
- "GPAI" / "general-purpose" → Chapter V
- "transparency" → Article 52
- "biometric" → Article 5, Annex III
- "technical documentation" → Annex IV

---

## 💡 使用示例

### Python + LangChain

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 加载文档
loader = DirectoryLoader(
    "Markdown_for_RAG/",
    glob="**/*.md",
    show_progress=True
)
documents = loader.load()

# 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\\n### ", "\\n## ", "\\n\\n", "\\n", " "]
)
chunks = text_splitter.split_documents(documents)

# 创建向量库
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./eu_ai_act_vectorstore"
)

# 查询示例
query = "What are the requirements for high-risk AI systems?"
results = vectorstore.similarity_search(query, k=5)
```

### Python + llamaindex

```python
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.node_parser import SimpleNodeParser

# 加载文档
documents = SimpleDirectoryReader("Markdown_for_RAG/").load_data()

# 创建节点解析器
parser = SimpleNodeParser.from_defaults(
    chunk_size=1024,
    chunk_overlap=100
)

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    node_parser=parser
)

# 查询
query_engine = index.as_query_engine()
response = query_engine.query(
    "What AI practices are prohibited under the EU AI Act?"
)
print(response)
```

---

## 📊 文档统计

| 类别 | 文件数 | 总大小 | 平均大小 |
|------|--------|--------|----------|
| P0 优先级 | 3 | 150.1 KB | 50.0 KB |
| P1 优先级 | 3 | 80.4 KB | 26.8 KB |
| P2 优先级 | 2 | 270.0 KB | 135.0 KB |
| **总计** | **8** | **500.5 KB** | **62.6 KB** |

**预估token数:** 约125,000 tokens (按GPT-4标准)

---

## 🔄 更新说明

- **版本:** 基于Official Journal L_202401689 (2024-07-12)
- **语言:** 英文
- **格式:** Markdown (UTF-8)
- **最后更新:** 2025-02-12

---

## ⚠️ 使用须知

1. **官方文本:** 本文档来源于EUR-Lex官方PDF
2. **法律效力:** Markdown版本仅供参考，法律效力以官方PDF为准
3. **提取准确性:** 已尽力保证准确，但建议关键内容核对原文
4. **商业使用:** 遵守EU相关版权和使用规定

---

## 📞 技术支持

如需完整PDF版本，请查看父目录中的备份文件。

**Happy RAG Building! 🚀**
