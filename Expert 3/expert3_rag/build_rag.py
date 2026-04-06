"""
build_rag.py
Expert 3 RAG Knowledge Base - Ingestion Script

Chunks the three UN/UNESCO markdown files by section (## headers),
embeds each chunk with all-MiniLM-L6-v2, and stores everything in a
persistent ChromaDB collection named "expert3_un_context".

Run once (or re-run to rebuild):
    pip install chromadb sentence-transformers
    python build_rag.py
"""

import re
import hashlib
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_DIR      = "./chroma_db"
COLLECTION_NAME = "expert3_un_context"
EMBED_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"

SOURCE_FILES = [
    "un_charter_principles.md",
    "un_data_protection.md",
    "unesco_ai_ethics.md",
]

# ─── CHUNKING ────────────────────────────────────────────────────────────────

def parse_retrieval_tags(md_text: str) -> list[str]:
    """Extract backtick-wrapped tags from the ## RAG Retrieval Tags section."""
    match = re.search(r"## RAG Retrieval Tags\s*\n(.*?)(?:\n##|\Z)", md_text, re.DOTALL)
    if not match:
        return []
    tag_block = match.group(1)
    return re.findall(r"`([^`]+)`", tag_block)


def chunk_by_sections(filepath: Path) -> list[dict]:
    """
    Split a markdown file on ## headers.
    Returns a list of chunk dicts with keys:
      source, section, content, tags, chunk_id
    """
    text = filepath.read_text(encoding="utf-8")
    filename = filepath.name

    # Extract global RAG tags (from the last section)
    global_tags = parse_retrieval_tags(text)

    # Split on lines that start with exactly "## "
    # Keep the header line with its content block
    parts = re.split(r"(?m)^(## .+)$", text)
    # parts: [preamble, header1, body1, header2, body2, ...]

    chunks = []

    # Preamble (before first ## header) - treat as a single chunk titled "Overview"
    preamble = parts[0].strip()
    if preamble:
        chunks.append({
            "source":  filename,
            "section": "Overview",
            "content": preamble,
            "tags":    global_tags,
        })

    # Paired (header, body) sections
    for i in range(1, len(parts) - 1, 2):
        header = parts[i].lstrip("# ").strip()
        body   = parts[i + 1].strip() if i + 1 < len(parts) else ""

        # Skip metadata-only sections (file header lines and retrieval tags)
        skip_prefixes = (
            "RAG Retrieval Tags",
            "Source:",
            "Applies to:",
            "Note:",
            "Purpose:",
            "Adopted by",
        )
        if any(header.startswith(p) for p in skip_prefixes):
            continue

        # Merge tags: global tags + any inline backtick words in the body
        inline_tags = re.findall(r"`([^`]+)`", body)
        combined_tags = list(dict.fromkeys(global_tags + inline_tags))  # dedup, order-preserved

        chunks.append({
            "source":  filename,
            "section": header,
            "content": (header + "\n\n" + body).strip(),
            "tags":    combined_tags,
        })

    return chunks


def make_chunk_id(source: str, section: str) -> str:
    key = f"{source}::{section}"
    return hashlib.md5(key.encode()).hexdigest()


# ─── MAIN ────────────────────────────────────────────────────────────────────

def build() -> None:
    print("=" * 55)
    print("Expert 3 RAG - Building Knowledge Base")
    print("=" * 55)

    # Validate source files
    base = Path(__file__).parent
    missing = [f for f in SOURCE_FILES if not (base / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing source files: {missing}\n"
            f"Expected in: {base}"
        )

    # Collect all chunks
    all_chunks: list[dict] = []
    for filename in SOURCE_FILES:
        fp     = base / filename
        chunks = chunk_by_sections(fp)
        print(f"\n  {filename}: {len(chunks)} sections")
        for c in chunks:
            print(f"    [{c['section'][:60]}]  tags={len(c['tags'])}")
        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")

    # ChromaDB client (persistent)
    chroma_path = str(base / "chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)

    # Delete existing collection to allow clean rebuild
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"\nDropped existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Ingest in one batch
    ids        = [make_chunk_id(c["source"], c["section"]) for c in all_chunks]
    documents  = [c["content"] for c in all_chunks]
    metadatas  = [
        {
            "source":  c["source"],
            "section": c["section"],
            "tags":    ", ".join(c["tags"]),       # ChromaDB requires string metadata
        }
        for c in all_chunks
    ]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)

    print(f"\n[OK] Ingested {len(ids)} chunks into '{COLLECTION_NAME}'")
    print(f"  Persistent storage: {chroma_path}")
    print("\nDone. Run test_rag.py to verify retrieval.")


if __name__ == "__main__":
    build()
