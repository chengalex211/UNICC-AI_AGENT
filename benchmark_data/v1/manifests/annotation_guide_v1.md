# Annotation Guide v1

Use this guide with `annotation_template_v1.csv`.

## Workflow

1. Run:
   - `python3 benchmark_annotation_tools.py export-template`
2. Fill `benchmark_data/v1/manifests/annotation_template_v1.csv`
3. Mark reviewed rows as:
   - `review_status = approved` (or `done` / `accepted`)
4. Merge:
   - `python3 benchmark_annotation_tools.py apply-annotations`

## Field Rules

- `gold_recommendation`: `APPROVE | REVIEW | REJECT`
- `gold_human_review_required`: `true | false`
- Multi-value fields use `||` separator:
  - `gold_must_hit_findings`
  - `gold_must_citations`
  - `gold_must_principles`

## Per-expert expectations

- E1:
  - At least 2 security findings in `gold_must_hit_findings`
- E2:
  - Add at least 1 legal citation in `gold_must_citations`
- E3:
  - Add at least 1 UN principle in `gold_must_principles`
- Council:
  - Findings should reference cross-expert synthesis quality

## Quality bar

- High-risk rows (`REJECT`) should have specific, evidence-like findings.
- Avoid generic findings such as "needs improvement".
- If uncertain, set `review_status = todo` and leave notes.

