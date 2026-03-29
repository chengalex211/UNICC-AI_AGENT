"""
query_rag.py
Expert 3 RAG Knowledge Base — Retrieval Module

Public API:
    from query_rag import retrieve

    results = retrieve("Does the AI treat users equally regardless of nationality?")
    # returns:
    # [
    #   {"source": "un_charter_principles.md", "section": "Article 1 ...", "content": "..."},
    #   ...
    # ]

Integration note:
    At Expert 3 inference time, inject the returned chunks into the system
    prompt context alongside the LoRA adapter output.
    Typical usage: retrieve(query, top_k=3)
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_DIR      = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "expert3_un_context"
EMBED_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_TOP_K   = 3

# Keyword boost: if a query word matches a chunk's tags, bump its rank score
TAG_BOOST_WEIGHT = 0.15   # additive boost to normalised similarity score


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
    """
    Return a small additive score if any query word matches a retrieval tag.
    Both query and tags are lowercased for comparison.
    """
    if not tags_str:
        return 0.0
    query_words = set(re.findall(r"\b\w+\b", query.lower()))
    tag_words   = set(re.findall(r"\b\w+\b", tags_str.lower()))
    overlap     = query_words & tag_words
    if not overlap:
        return 0.0
    # Boost proportional to fraction of query words matched (capped)
    return min(TAG_BOOST_WEIGHT, TAG_BOOST_WEIGHT * len(overlap) / max(len(query_words), 1))


# ─── PUBLIC API ──────────────────────────────────────────────────────────────

def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Query the Expert 3 RAG knowledge base.

    Parameters
    ----------
    query  : natural-language question or keyword string
    top_k  : number of chunks to return (default 3)

    Returns
    -------
    List of dicts, ordered by relevance (highest first):
        [
          {
            "source":  "filename.md",
            "section": "section title",
            "content": "full chunk text",
            "score":   0.87,          # cosine similarity + tag boost
            "tags":    ["tag1", ...]
          },
          ...
        ]
    """
    if not query or not query.strip():
        return []

    collection = _get_collection()

    # Fetch extra candidates so tag-boosted re-ranking is effective
    n_candidates = min(top_k * 3, collection.count())
    if n_candidates == 0:
        return []

    result = collection.query(
        query_texts=[query],
        n_results=n_candidates,
        include=["documents", "metadatas", "distances"],
    )

    docs      = result["documents"][0]
    metas     = result["metadatas"][0]
    distances = result["distances"][0]     # cosine distance (lower = more similar)

    candidates = []
    for doc, meta, dist in zip(docs, metas, distances):
        # Convert distance to similarity (cosine distance ∈ [0,2] with hnsw:cosine)
        similarity = 1.0 - (dist / 2.0)
        tags_str   = meta.get("tags", "")
        boosted    = similarity + _tag_boost(query, tags_str)

        candidates.append({
            "source":  meta.get("source", ""),
            "section": meta.get("section", ""),
            "content": doc,
            "score":   round(min(boosted, 1.0), 4),
            "tags":    [t.strip() for t in tags_str.split(",") if t.strip()],
        })

    # Re-rank by boosted score, return top_k
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_k]


def format_for_prompt(results: list[dict]) -> str:
    """
    Format retrieved chunks for injection into Expert 3's system prompt.

    Returns a string block like:
        [Context 1 — un_charter_principles.md | Article 1 ...]
        <chunk text>

        [Context 2 — ...]
        ...
    """
    if not results:
        return "(No relevant regulatory context found.)"

    lines = []
    for i, r in enumerate(results, 1):
        header = f"[Context {i} — {r['source']} | {r['section']}]"
        lines.append(header)
        lines.append(r["content"])
        lines.append("")
    return "\n".join(lines).strip()


# ─── STANDALONE DEMO ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "human rights non-discrimination"
    print(f"Query: {query!r}\n")
    results = retrieve(query)
    print(format_for_prompt(results))
    print(f"\n({len(results)} chunks returned)")
