"""
test_rag.py
Expert 3 RAG Knowledge Base — Retrieval Verification

Runs 5 test queries covering each source file and cross-document cases.
Each query asserts that the expected source file appears in the top results.

Run:
    python test_rag.py

Expected output: 5/5 PASS
"""

from query_rag import retrieve, format_for_prompt

# ─── TEST CASES ──────────────────────────────────────────────────────────────
# Format: (query_string, must_contain_source, description)

TEST_CASES = [
    (
        "Does the AI treat users equally regardless of nationality or language?",
        "un_charter_principles.md",
        "UN Charter — equal rights / non-discrimination",
    ),
    (
        "AI system sends personal data to external APIs without consent",
        "un_data_protection.md",
        "UN Data Protection — third-party transfers / Principle 9",
    ),
    (
        "Can the AI be used for mass surveillance or social scoring?",
        "unesco_ai_ethics.md",
        "UNESCO — peaceful use / proportionality",
    ),
    (
        "human oversight and accountability for AI decisions",
        "unesco_ai_ethics.md",
        "UNESCO — human oversight / accountability",
    ),
    (
        "data retention and deletion of personal data processed by UN organizations",
        "un_data_protection.md",
        "UN Data Protection — retention Principle 4",
    ),
]


# ─── RUNNER ──────────────────────────────────────────────────────────────────

def run_tests() -> None:
    print("=" * 60)
    print("Expert 3 RAG — Retrieval Verification (5 test queries)")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    for i, (query, expected_source, description) in enumerate(TEST_CASES, 1):
        results = retrieve(query, top_k=3)
        sources = [r["source"] for r in results]
        top     = results[0] if results else {}

        ok = expected_source in sources
        status = "PASS ✓" if ok else "FAIL ✗"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"[{i}/5] {status}  {description}")
        print(f"       Query:    {query!r}")
        print(f"       Expected: {expected_source}")
        print(f"       Got:      {sources}")
        if top:
            print(f"       Top hit:  [{top['section']}] score={top['score']}")
        print()

    print("─" * 60)
    print(f"Result: {passed}/5 passed, {failed}/5 failed")

    if failed == 0:
        print("\nAll tests passed. RAG knowledge base is ready for Expert 3.")
    else:
        print(
            "\nSome tests failed. Check that build_rag.py ran successfully "
            "and the chroma_db/ directory is populated."
        )

    print()

    # ── Bonus: show formatted prompt injection for first query ────────────────
    print("─" * 60)
    print("Sample prompt injection output (query 1):\n")
    q = TEST_CASES[0][0]
    r = retrieve(q, top_k=3)
    print(format_for_prompt(r))


if __name__ == "__main__":
    run_tests()
