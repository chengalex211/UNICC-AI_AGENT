"""
test_rag_expert2.py
Expert 2 RAG Knowledge Base — Verification Script

运行前必须先执行 build_rag_expert2.py。

测试覆盖：
  1. 知识库基本信息（chunk 总数、各管辖区分布）
  2. 通用检索：P0 优先级 boost 验证
  3. 9 个合规维度各 1 条 retrieve_for_dimension() 测试
  4. jurisdiction_filter 过滤测试
  5. p0_only 过滤测试
  6. format_for_prompt() 输出格式验证

运行：
    python test_rag_expert2.py
"""

import sys
from collections import Counter

try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    from query_rag_expert2 import (
        retrieve,
        retrieve_for_dimension,
        retrieve_multi_dimension,
        format_for_prompt,
        COLLECTION_NAME,
        CHROMA_DIR,
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Run: pip install chromadb sentence-transformers")
    sys.exit(1)

PASS  = "✓"
FAIL  = "✗"
WARN  = "⚠"

results_log: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    results_log.append((name, condition, detail))
    icon = PASS if condition else FAIL
    print(f"  {icon} {name}" + (f"  — {detail}" if detail else ""))


# ─── TEST 1：知识库基本信息 ────────────────────────────────────────────────────

def test_collection_stats():
    print("\n[1] Collection Stats")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    try:
        col = client.get_collection(COLLECTION_NAME, embedding_function=embed_fn)
    except Exception as e:
        check("Collection exists", False, str(e))
        return

    total = col.count()
    check("Collection exists", True, f"name={COLLECTION_NAME!r}")
    check("Has chunks",        total > 0,  f"{total} chunks")
    check("Minimum 50 chunks", total >= 50, f"got {total}")

    # 按 jurisdiction 统计
    all_meta = col.get(include=["metadatas"])["metadatas"]
    by_jur = Counter(m.get("jurisdiction", "?") for m in all_meta)
    by_pri = Counter(m.get("priority", "?") for m in all_meta)

    print(f"       Breakdown by jurisdiction: {dict(by_jur)}")
    print(f"       Breakdown by priority:     {dict(by_pri)}")

    check("Has EU_AI_Act chunks", by_jur.get("EU_AI_Act", 0) > 0,
          f"{by_jur.get('EU_AI_Act',0)} chunks")
    check("Has GDPR chunks",      by_jur.get("GDPR", 0) > 0,
          f"{by_jur.get('GDPR',0)} chunks")
    check("Has P0 chunks",        by_pri.get("P0", 0) > 0,
          f"{by_pri.get('P0',0)} P0 chunks")


# ─── TEST 2：通用检索 + P0 boost ─────────────────────────────────────────────

def test_basic_retrieve():
    print("\n[2] Basic Retrieve + P0 Boost")

    results = retrieve("automated decision-making profiling GDPR Article 22")
    check("Returns results",         len(results) > 0, f"{len(results)} results")
    check("Returns up to 5",         len(results) <= 5)
    check("Result has required keys", all(
        {"source","section","jurisdiction","priority","content","score","tags"}.issubset(r.keys())
        for r in results
    ))

    # P0 boost：第一条结果应来自 P0 核心法规
    if results:
        check("Top result is P0",   results[0]["priority"] == "P0",
              f"got priority={results[0]['priority']!r} source={results[0]['source']!r}")
        check("Score in [0,1]",     0.0 <= results[0]["score"] <= 1.0,
              f"score={results[0]['score']}")

    # 空查询应返回空列表
    empty = retrieve("")
    check("Empty query returns []", empty == [])


# ─── TEST 3：9 个合规维度 ─────────────────────────────────────────────────────

_DIMENSION_EXPECTED_JURISDICTIONS = {
    "automated_decision_making": {"GDPR", "EU_AI_Act"},
    "high_risk_classification":  {"EU_AI_Act"},
    "data_protection":           {"GDPR"},
    "transparency":              {"EU_AI_Act", "GDPR"},
    "human_oversight":           {"EU_AI_Act", "NIST", "UNESCO"},
    "security_robustness":       {"EU_AI_Act", "OWASP", "NIST"},
    "bias_fairness":             {"UNESCO", "GDPR", "UN"},
    "accountability":            {"NIST", "EU_AI_Act", "GDPR"},
    "data_governance":           {"EU_AI_Act", "GDPR"},
}

_AGENT_DESC = (
    "AI-powered loan application screening system that automatically "
    "approves or rejects personal loan applications based on applicant data."
)


def test_dimension_retrieval():
    print("\n[3] Dimension Retrieval (9 dimensions)")

    for dim, expected_jurs in _DIMENSION_EXPECTED_JURISDICTIONS.items():
        results = retrieve_for_dimension(dim, _AGENT_DESC, top_k=5)
        got_jurs = {r["jurisdiction"] for r in results}

        has_results = len(results) > 0
        has_expected = bool(got_jurs & expected_jurs)

        check(
            f"dim={dim}",
            has_results and has_expected,
            f"{len(results)} results | jurisdictions={sorted(got_jurs)}"
            + (f" | MISSING {expected_jurs - got_jurs}" if not has_expected else ""),
        )


# ─── TEST 4：jurisdiction_filter ──────────────────────────────────────────────

def test_jurisdiction_filter():
    print("\n[4] jurisdiction_filter")

    for jur in ["EU_AI_Act", "GDPR", "NIST"]:
        results = retrieve("AI system risk compliance", jurisdiction_filter=jur)
        all_match = all(r["jurisdiction"] == jur for r in results)
        check(
            f"filter={jur!r}",
            all_match,
            f"{len(results)} results, all jurisdiction=={jur}: {all_match}"
        )


# ─── TEST 5：p0_only ──────────────────────────────────────────────────────────

def test_p0_filter():
    print("\n[5] p0_only filter")

    results = retrieve("AI system compliance", p0_only=True, top_k=10)
    all_p0 = all(r["priority"] == "P0" for r in results)
    check("p0_only returns only P0", all_p0, f"{len(results)} results")


# ─── TEST 6：format_for_prompt ────────────────────────────────────────────────

def test_format_for_prompt():
    print("\n[6] format_for_prompt")

    results = retrieve("GDPR automated decision", top_k=3)
    formatted = format_for_prompt(results)

    check("Returns string",            isinstance(formatted, str))
    check("Contains [Legal Context",   "[Legal Context" in formatted)
    check("Contains jurisdiction",     "EU_AI_Act" in formatted or "GDPR" in formatted)

    # 含维度标注版本
    formatted_dim = format_for_prompt(results, dimension="automated_decision_making")
    check("Contains dimension label",  "[Compliance Dimension:" in formatted_dim)

    # 空结果
    empty_fmt = format_for_prompt([])
    check("Empty returns fallback msg","No relevant" in empty_fmt)


# ─── TEST 7：retrieve_multi_dimension ─────────────────────────────────────────

def test_multi_dimension():
    print("\n[7] retrieve_multi_dimension")

    dims = ["automated_decision_making", "data_protection", "transparency"]
    multi = retrieve_multi_dimension(dims, _AGENT_DESC, top_k_per_dim=3)

    check("Returns dict",         isinstance(multi, dict))
    check("Keys match dims",      set(multi.keys()) == set(dims))
    check("Each dim has results", all(len(v) > 0 for v in multi.values()),
          str({k: len(v) for k, v in multi.items()}))


# ─── SUMMARY ─────────────────────────────────────────────────────────────────

def print_summary():
    passed  = sum(1 for _, ok, _ in results_log if ok)
    failed  = sum(1 for _, ok, _ in results_log if not ok)
    total   = len(results_log)

    print("\n" + "=" * 55)
    print(f"Expert 2 RAG Test Summary: {passed}/{total} passed")
    print("=" * 55)

    if failed:
        print("\nFailed checks:")
        for name, ok, detail in results_log:
            if not ok:
                print(f"  {FAIL} {name}" + (f"  — {detail}" if detail else ""))

    if failed == 0:
        print("All tests passed. RAG knowledge base is ready.")
    elif failed <= 2:
        print(f"{WARN} Minor issues — knowledge base is usable but review failures above.")
    else:
        print("RAG knowledge base has issues. Re-run build_rag_expert2.py.")


# ─── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Expert 2 RAG — Verification Tests")
    print("=" * 55)
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Storage    : {CHROMA_DIR}")

    test_collection_stats()
    test_basic_retrieve()
    test_dimension_retrieval()
    test_jurisdiction_filter()
    test_p0_filter()
    test_format_for_prompt()
    test_multi_dimension()

    print_summary()
