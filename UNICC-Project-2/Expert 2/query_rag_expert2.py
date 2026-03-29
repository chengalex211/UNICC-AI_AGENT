"""
query_rag_expert2.py
Expert 2 RAG Knowledge Base — Retrieval Module

公开 API：
    from query_rag_expert2 import retrieve, retrieve_for_dimension, format_for_prompt

    # 通用检索
    results = retrieve("automated decision-making GDPR Article 22")

    # 按合规维度检索（Expert 2 推理时使用）
    results = retrieve_for_dimension("automated_decision_making", agent_description)

    # 格式化注入 system prompt
    context = format_for_prompt(results)

与 Expert 3 query_rag.py 的核心区别：
  1. P0 优先级 boost（核心法规比补充文件权重更高）
  2. retrieve_for_dimension()：9 个合规维度各有定向查询策略
  3. jurisdiction_filter / p0_only 过滤参数
  4. format_for_prompt() 输出包含管辖区信息
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_DIR      = str(Path(__file__).parent / "chroma_db_expert2")
COLLECTION_NAME = "expert2_legal_compliance"
EMBED_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K   = 5
TAG_BOOST       = 0.20   # 法律术语精确匹配比 Expert 3 更重要
P0_BOOST        = 0.10   # P0 核心法规额外加分


# ─── 9 个合规维度的定向查询策略 ───────────────────────────────────────────────
# 每个维度提供 2-3 条最精准的子查询，覆盖该维度的核心法规条款

DIMENSION_QUERIES: dict[str, list[str]] = {
    "automated_decision_making": [
        "automated individual decision-making profiling GDPR Article 22",
        "right to explanation automated decision AI system output",
        "EU AI Act prohibited real-time biometric automated decision",
    ],
    "high_risk_classification": [
        "EU AI Act high-risk AI system classification Annex III",
        "EU AI Act prohibited practices unacceptable risk Article 5",
        "high-risk AI requirements conformity assessment documentation",
    ],
    "data_protection": [
        "GDPR lawfulness consent special categories Article 6 Article 9",
        "data minimization purpose limitation storage limitation Article 5",
        "privacy by design data protection by default Article 25",
    ],
    "transparency": [
        "EU AI Act transparency obligations Article 13 documentation deployers",
        "GDPR transparency information Article 13 14 data subjects",
        "AI system explainability human-understandable output",
    ],
    "human_oversight": [
        "EU AI Act human oversight Article 14 automation bias",
        "NIST AI RMF GOVERN human oversight control intervention",
        "UNESCO AI ethics human agency meaningful control",
    ],
    "security_robustness": [
        "EU AI Act accuracy robustness cybersecurity Article 15",
        "OWASP LLM Top 10 prompt injection adversarial attack",
        "NIST adversarial machine learning threat taxonomy",
    ],
    "bias_fairness": [
        "non-discrimination bias fairness UNESCO AI ethics",
        "GDPR Article 9 special categories discrimination bias",
        "UN human rights digital technology algorithmic discrimination",
    ],
    "accountability": [
        "NIST AI RMF GOVERN accountability organizational risk",
        "EU AI Act quality management system Article 17 deployer obligations",
        "GDPR controller processor accountability Article 24 records",
    ],
    "data_governance": [
        "EU AI Act data governance training data Article 10",
        "GDPR data quality accuracy Article 5(1)(d) records processing",
        "data documentation provenance bias detection training data",
    ],
}


# ─── CHROMA CLIENT (lazy singleton) ──────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )


# ─── TAG BOOST ───────────────────────────────────────────────────────────────

def _tag_boost(query: str, tags_str: str) -> float:
    if not tags_str:
        return 0.0
    query_words = set(re.findall(r"\b\w+\b", query.lower()))
    tag_words   = set(re.findall(r"\b\w+\b", tags_str.lower()))
    overlap     = query_words & tag_words
    if not overlap:
        return 0.0
    return min(TAG_BOOST, TAG_BOOST * len(overlap) / max(len(query_words), 1))


# ─── PUBLIC API ──────────────────────────────────────────────────────────────

def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    jurisdiction_filter: str | None = None,
    p0_only: bool = False,
) -> list[dict]:
    """
    检索 Expert 2 法规知识库。

    Parameters
    ----------
    query               : 评估问题或关键词
    top_k               : 返回条款数（默认 5）
    jurisdiction_filter : "EU_AI_Act" | "GDPR" | "NIST" | "OWASP" | "UNESCO" | "UN"
    p0_only             : 只返回 P0 核心法规（排除补充文件）

    Returns
    -------
    List[dict] — 按相关度排序：
        source, section, jurisdiction, priority, content, score, tags
    """
    if not query or not query.strip():
        return []

    collection = _get_collection()
    n_candidates = min(top_k * 4, collection.count())
    if n_candidates == 0:
        return []

    # 构建 ChromaDB where 过滤（只支持 $eq）
    where = _build_where(jurisdiction_filter, p0_only)

    result = collection.query(
        query_texts=[query],
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"],
        where=where,
    )

    docs      = result["documents"][0]
    metas     = result["metadatas"][0]
    distances = result["distances"][0]

    candidates = []
    for doc, meta, dist in zip(docs, metas, distances):
        similarity = 1.0 - (dist / 2.0)
        tags_str   = meta.get("tags", "")
        priority   = meta.get("priority", "P1")

        score = (
            similarity
            + _tag_boost(query, tags_str)
            + (P0_BOOST if priority == "P0" else 0.0)
        )

        candidates.append({
            "source":       meta.get("source", ""),
            "section":      meta.get("section", ""),
            "jurisdiction": meta.get("jurisdiction", ""),
            "priority":     priority,
            "content":      doc,
            "score":        round(min(score, 1.0), 4),
            "tags":         [t.strip() for t in tags_str.split(",") if t.strip()],
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


def retrieve_for_dimension(
    dimension: str,
    agent_description: str = "",
    top_k: int = 5,
) -> list[dict]:
    """
    Expert 2 专用：按合规维度定向检索最相关法规条款。

    每个维度有 2-3 条精准子查询，多查询结果合并去重后按 score 排序。

    Parameters
    ----------
    dimension         : 9 个合规维度之一（见 DIMENSION_QUERIES）
    agent_description : 被评估系统的描述，用于补充语义检索
    top_k             : 最终返回条款数

    用法示例：
        for dim in ["automated_decision_making", "data_protection", "transparency"]:
            chunks = retrieve_for_dimension(dim, agent_desc)
            context = format_for_prompt(chunks, dimension=dim)
    """
    queries = DIMENSION_QUERIES.get(dimension, [])
    if not queries:
        # 未知维度：直接用 agent_description 检索
        return retrieve(agent_description or dimension, top_k=top_k)

    # 如果有 agent_description，追加一条基于描述的语义查询
    if agent_description:
        queries = queries + [agent_description]

    seen = set()
    all_results: list[dict] = []

    for q in queries:
        for r in retrieve(q, top_k=3):
            key = f"{r['source']}::{r['section']}"
            if key not in seen:
                seen.add(key)
                all_results.append(r)

    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]


def retrieve_multi_dimension(
    dimensions: list[str],
    agent_description: str,
    top_k_per_dim: int = 3,
) -> dict[str, list[dict]]:
    """
    同时检索多个维度，返回以维度名为键的字典。

    用于 Expert 2 完整评估流程：
        results = retrieve_multi_dimension(
            ["automated_decision_making", "data_protection", "transparency"],
            agent_description
        )
        for dim, chunks in results.items():
            ...
    """
    return {
        dim: retrieve_for_dimension(dim, agent_description, top_k=top_k_per_dim)
        for dim in dimensions
    }


def format_for_prompt(
    results: list[dict],
    dimension: str | None = None,
) -> str:
    """
    格式化检索结果，用于注入 Expert 2 的 system prompt。

    比 Expert 3 多输出 jurisdiction 信息，
    让模型明确知道引用的是 EU 法规还是国际标准。

    Parameters
    ----------
    results   : retrieve() 或 retrieve_for_dimension() 的返回值
    dimension : 可选，在输出头部标注当前维度
    """
    if not results:
        return "(No relevant legal provisions found.)"

    lines = []
    if dimension:
        lines.append(f"[Compliance Dimension: {dimension}]")
        lines.append("")

    for i, r in enumerate(results, 1):
        header = (
            f"[Legal Context {i} — {r['source']} | "
            f"{r['section']} | {r['jurisdiction']} | "
            f"Priority: {r['priority']}]"
        )
        lines.append(header)
        lines.append(r["content"])
        lines.append("")

    return "\n".join(lines).strip()


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _build_where(jurisdiction: str | None, p0_only: bool) -> dict | None:
    """
    构建 ChromaDB metadata 过滤条件。
    ChromaDB 只支持 $eq / $ne / $gt / $lt，不支持字符串 $contains。
    所以用 build 时预计算的布尔字段来过滤。
    """
    conditions = []

    if jurisdiction:
        conditions.append({"jurisdiction": {"$eq": jurisdiction}})

    if p0_only:
        conditions.append({"is_p0": {"$eq": True}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


# ─── STANDALONE DEMO ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "dim":
        # 按维度检索演示
        dim = sys.argv[2] if len(sys.argv) > 2 else "automated_decision_making"
        desc = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        print(f"Dimension: {dim!r}\n")
        results = retrieve_for_dimension(dim, desc)
        print(format_for_prompt(results, dimension=dim))
        print(f"\n({len(results)} chunks returned)")
    else:
        # 通用检索演示
        query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "GDPR Article 22 automated decision"
        print(f"Query: {query!r}\n")
        results = retrieve(query)
        print(format_for_prompt(results))
        print(f"\n({len(results)} chunks returned)")
