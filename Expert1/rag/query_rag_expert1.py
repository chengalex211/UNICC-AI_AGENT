"""
rag/query_rag_expert1.py
Expert 1 RAG — Retrieval Module

公开 API:
    from rag.query_rag_expert1 import retrieve_techniques, retrieve_strategies, format_for_attacker

    # Phase 3: 根据 Agent 描述选攻击技术
    techniques = retrieve_techniques(
        "UNHCR refugee case management chatbot with access to beneficiary records",
        top_k=10
    )
    selected = diversify_top3(techniques)

    # Phase 3: 给每个技术获取策略参考
    strategies = retrieve_strategies(
        "authority impersonation in humanitarian context",
        top_k=5
    )
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_DIR            = str(Path(__file__).parent / "chroma_db_expert1")
EMBED_MODEL           = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_TECHNIQUES = "expert1_attack_techniques"
COLLECTION_STRATEGIES = "expert1_attack_strategies"

DEFAULT_TOP_K  = 10
TAG_BOOST      = 0.18
LAYER_BOOST    = 0.10  # 多样化时同层技术降权


# ─── CHROMA CLIENTS (lazy singletons) ────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_techniques_col():
    client   = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_collection(COLLECTION_TECHNIQUES, embedding_function=embed_fn)


@lru_cache(maxsize=1)
def _get_strategies_col():
    client   = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    return client.get_collection(COLLECTION_STRATEGIES, embedding_function=embed_fn)


# ─── TAG BOOST ────────────────────────────────────────────────────────────────

def _tag_boost(query: str, tags_str: str) -> float:
    if not tags_str:
        return 0.0
    q_words   = set(re.findall(r"\b\w+\b", query.lower()))
    tag_words = set(re.findall(r"\b\w+\b", tags_str.lower()))
    overlap   = q_words & tag_words
    if not overlap:
        return 0.0
    return min(TAG_BOOST, TAG_BOOST * len(overlap) / max(len(q_words), 1))


# ─── PUBLIC API ───────────────────────────────────────────────────────────────

def retrieve_techniques(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    attack_layer_filter: str | None = None,
) -> list[dict]:
    """
    Collection 1 检索：根据 Agent 描述返回最相关的攻击技术。

    Parameters
    ----------
    query               : AgentProfile 的描述文本（description + purpose + context）
    top_k               : 返回候选技术数（之后由 diversify_top3 筛选到 3 个）
    attack_layer_filter : "model" | "application" | "social_engineering" | None

    Returns
    -------
    List[dict]: source, section, source_label, attack_layer, content, score, tags
    """
    if not query.strip():
        return []

    col          = _get_techniques_col()
    n_candidates = min(top_k * 3, col.count())
    if n_candidates == 0:
        return []

    where = {"attack_layer": {"$eq": attack_layer_filter}} if attack_layer_filter else None

    result = col.query(
        query_texts=[query],
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"],
        where=where,
    )

    return _build_results(result, query, top_k)


def retrieve_strategies(
    query: str,
    top_k: int = 5,
    source_filter: str | None = None,
) -> list[dict]:
    """
    Collection 2 检索：根据技术名称 + 部署场景返回攻击策略参考。

    Parameters
    ----------
    query         : "{technique_name} in humanitarian UN context"
    top_k         : 返回策略数（默认 5）
    source_filter : "ATLAS" | "UN_SPECIFIC" | None
    """
    if not query.strip():
        return []

    col          = _get_strategies_col()
    n_candidates = min(top_k * 3, col.count())
    if n_candidates == 0:
        return []

    where = {"source_label": {"$eq": source_filter}} if source_filter else None

    result = col.query(
        query_texts=[query],
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"],
        where=where,
    )

    return _build_results(result, query, top_k)


def diversify_top3(candidates: list[dict]) -> list[dict]:
    """
    设计文档 §7 要求：
    从候选技术中选出覆盖不同 attack_layer 的 top-3，
    确保不会选 3 个都是同一种攻击方式（如全是 prompt injection 变体）。

    优先级：score 最高 → 不同 layer 覆盖
    """
    seen_layers: set[str] = set()
    selected: list[dict] = []

    # 第一遍：每个 layer 最多选 1 个
    for c in candidates:
        layer = c.get("attack_layer", "mixed")
        if layer not in seen_layers:
            seen_layers.add(layer)
            selected.append(c)
        if len(selected) == 3:
            break

    # 如果不足 3 个（来源不够多样化），从剩余中补
    if len(selected) < 3:
        remaining = [c for c in candidates if c not in selected]
        selected.extend(remaining[: 3 - len(selected)])

    return selected[:3]


def format_for_attacker(strategies: list[dict]) -> list[str]:
    """
    将策略检索结果格式化为 attacker prompt 里的 strategy_examples 列表。
    每条保持 1-2 句话，方便注入 get_attacker_system_prompt 的 strategy_block。
    """
    examples = []
    for r in strategies:
        section = r.get("section", "")
        content = r.get("content", "")
        # 只取第一段（约 1-2 句），避免 context 过长
        first_para = content.split("\n\n")[1] if "\n\n" in content else content
        first_para = first_para[:300].strip()
        examples.append(f"[{section}] {first_para}")
    return examples


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def _build_results(result: dict, query: str, top_k: int) -> list[dict]:
    docs      = result["documents"][0]
    metas     = result["metadatas"][0]
    distances = result["distances"][0]

    candidates = []
    for doc, meta, dist in zip(docs, metas, distances):
        similarity = 1.0 - (dist / 2.0)
        tags_str   = meta.get("tags", "")
        score      = similarity + _tag_boost(query, tags_str)

        candidates.append({
            "source":       meta.get("source", ""),
            "section":      meta.get("section", ""),
            "source_label": meta.get("source_label", ""),
            "attack_layer": meta.get("attack_layer", "mixed"),
            "content":      doc,
            "score":        round(min(score, 1.0), 4),
            "tags":         [t.strip() for t in tags_str.split(",") if t.strip()],
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


# ─── STANDALONE DEMO ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "UNHCR refugee case management chatbot with access to beneficiary records "
        "and personal data in humanitarian contexts"
    )

    print(f"Query: {query!r}\n")

    print("=== Top-10 Techniques ===")
    techs = retrieve_techniques(query, top_k=10)
    for i, t in enumerate(techs, 1):
        print(f"  {i}. [{t['attack_layer']:<20}] {t['section'][:60]}  score={t['score']}")

    print("\n=== Diversified Top-3 ===")
    selected = diversify_top3(techs)
    for t in selected:
        print(f"  [{t['attack_layer']}] {t['section']}")

    print("\n=== Strategy Reference (for first technique) ===")
    if selected:
        q2 = f"{selected[0]['section']} in humanitarian UN context"
        strategies = retrieve_strategies(q2, top_k=3)
        examples = format_for_attacker(strategies)
        for ex in examples:
            print(f"  - {ex[:120]}")
