"""
rag/build_rag_expert1.py
Expert 1 RAG — Two-Collection Knowledge Base Builder

Collection 1: expert1_attack_techniques
  - ATLAS 61个技术（LLM/AI Agent 相关）
  - OWASP LLM Top 10 2025
  - NIST Adversarial ML Taxonomy
  用途：根据被测 Agent 描述，检索最相关的攻击技术

Collection 2: expert1_attack_strategies
  - ATLAS 52个真实案例
  - UN 特定攻击向量（UN-ATK-001 到 UN-ATK-015）
  用途：给 attacker LLM 提供具体攻击策略参考

运行：
    pip install chromadb sentence-transformers
    python rag/build_rag_expert1.py
"""

import re
import hashlib
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_DIR   = str(Path(__file__).parent / "chroma_db_expert1")
EMBED_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_TECHNIQUES = "expert1_attack_techniques"
COLLECTION_STRATEGIES = "expert1_attack_strategies"

BASE = Path(__file__).parent.parent  # Expert 1 目录

SOURCE_TECHNIQUES = [
    (BASE / "knowledge_base" / "attack_techniques" / "ATLAS_Techniques.md",   "ATLAS",  "model, application, social_engineering"),
    (BASE / "knowledge_base" / "attack_techniques" / "OWASP_LLM_Top10.md",    "OWASP",  "application, LLM_vulnerability"),
    (BASE / "knowledge_base" / "attack_techniques" / "NIST_Adversarial_ML.md","NIST",   "model, taxonomy"),
]

SOURCE_STRATEGIES = [
    (BASE / "knowledge_base" / "attack_strategies" / "ATLAS_Case_Studies.md",   "ATLAS",      "real_world_attack, case_study"),
    (BASE / "knowledge_base" / "attack_strategies" / "UN_Attack_Vectors.md",    "UN_SPECIFIC","social_engineering, humanitarian"),
]


# ─── CHUNKING ─────────────────────────────────────────────────────────────────

def chunk_by_sections(filepath: Path, source_label: str, relevance: str) -> list[dict]:
    """## 级别分块，每个 technique/case study = 1 chunk"""
    text = filepath.read_text(encoding="utf-8")
    filename = filepath.name

    global_tags = [t.strip() for t in relevance.split(",") if t.strip()]
    global_tags.append(source_label)

    # 从 RAG Retrieval Tags 区块提取额外标签
    tag_match = re.search(r"## RAG Retrieval Tags\s*\n(.*?)(?:\n##|\Z)", text, re.DOTALL)
    if tag_match:
        extra = re.findall(r"`([^`]+)`", tag_match.group(1))
        global_tags = list(dict.fromkeys(global_tags + extra))

    # 按 ## 分块
    parts = re.split(r"(?m)^(## .+)$", text)
    chunks = []

    for i in range(1, len(parts) - 1, 2):
        header_raw = parts[i]
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        header_clean = header_raw.lstrip("# ").strip()

        skip = ("RAG Retrieval Tags", "Source:", "Purpose:", "Overview")
        if any(header_clean.startswith(s) for s in skip):
            continue
        if len(body) < 50:
            continue

        # 从正文提取 ID 标签（AML.T0051, LLM01, UN-ATK-001 等）
        id_tags = re.findall(r"\b(AML\.[A-Z0-9.]+|LLM\d+|NIST-[A-Z]+|UN-ATK-\d+)\b", header_clean + " " + body)
        inline_tags = re.findall(r"`([^`]+)`", body)
        combined = list(dict.fromkeys(global_tags + id_tags + inline_tags))

        # 推断攻击层
        combined_text = (header_clean + " " + body).lower()
        if any(kw in combined_text for kw in ["prompt injection", "jailbreak", "output handling", "supply chain"]):
            attack_layer = "application"
        elif any(kw in combined_text for kw in ["model extraction", "poisoning", "evasion", "adversarial example"]):
            attack_layer = "model"
        elif any(kw in combined_text for kw in ["social engineering", "impersonation", "authority", "empathy", "urgency"]):
            attack_layer = "social_engineering"
        else:
            attack_layer = "mixed"

        enriched = (
            f"[Source: {filename} | {source_label} | Section: {header_clean}]\n\n"
            f"{header_clean}\n\n{body}"
        ).strip()

        chunks.append({
            "source":       filename,
            "section":      header_clean,
            "source_label": source_label,
            "attack_layer": attack_layer,
            "content":      enriched,
            "tags":         combined,
        })

    return chunks


def make_chunk_id(source: str, section: str, idx: int) -> str:
    key = f"{source}::{section}::{idx}"
    return hashlib.md5(key.encode()).hexdigest()


# ─── BUILD ────────────────────────────────────────────────────────────────────

def build_collection(
    client: chromadb.PersistentClient,
    embed_fn,
    collection_name: str,
    sources: list[tuple],
    label: str,
) -> int:
    all_chunks: list[dict] = []

    for filepath, source_label, relevance in sources:
        if not filepath.exists():
            print(f"    ⚠ MISSING: {filepath}")
            continue
        chunks = chunk_by_sections(filepath, source_label, relevance)
        print(f"    [{source_label:<12}] {filepath.name}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print(f"  ERROR: No chunks for {collection_name}")
        return 0

    try:
        client.delete_collection(collection_name)
        print(f"  Dropped existing '{collection_name}'")
    except Exception:
        pass

    col = client.create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 200
    for start in range(0, len(all_chunks), batch_size):
        batch = all_chunks[start : start + batch_size]
        col.add(
            ids=[make_chunk_id(c["source"], c["section"], start + j) for j, c in enumerate(batch)],
            documents=[c["content"] for c in batch],
            metadatas=[{
                "source":       c["source"],
                "section":      c["section"],
                "source_label": c["source_label"],
                "attack_layer": c["attack_layer"],
                "tags":         ", ".join(c["tags"]),
            } for c in batch],
        )
        print(f"    Ingested batch {start // batch_size + 1}: {len(batch)} chunks")

    print(f"  ✓ {len(all_chunks)} chunks → '{collection_name}'")
    return len(all_chunks)


def build():
    print("=" * 60)
    print("Expert 1 RAG — Building Attack Knowledge Base")
    print("=" * 60)

    client   = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    print(f"\n[Collection 1: {COLLECTION_TECHNIQUES}]")
    n1 = build_collection(client, embed_fn, COLLECTION_TECHNIQUES, SOURCE_TECHNIQUES, "techniques")

    print(f"\n[Collection 2: {COLLECTION_STRATEGIES}]")
    n2 = build_collection(client, embed_fn, COLLECTION_STRATEGIES, SOURCE_STRATEGIES, "strategies")

    print(f"\n{'='*60}")
    print(f"Done.  Techniques: {n1} chunks | Strategies: {n2} chunks")
    print(f"Storage: {CHROMA_DIR}")
    print("Run rag/query_rag_expert1.py to test retrieval.")


if __name__ == "__main__":
    build()
