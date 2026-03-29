# Benchmark Readiness v1

- status: `READY_FOR_MODEL_BENCHMARKING`
- total_rows: `80`
- unique_sample_ids: `80`
- high_risk_ratio: `0.938`

## Coverage
- by_target: `{'e3': 15, 'council': 10, 'e1': 40, 'e2': 15}`
- recommendation_distribution: `{'REVIEW': 41, 'REJECT': 34, 'APPROVE': 5}`
- risk_tier_distribution: `{'HIGH': 23, 'UNACCEPTABLE': 34, 'SIGNIFICANT': 15, 'LIMITED': 8}`

## Completeness
- missing_gold_recommendation: `0`
- missing_gold_human_review_required: `0`
- missing_must_hit_findings: `0`
- e2_missing_citations: `0`
- e3_missing_principles: `0`

## Blockers
- none

## Next Actions
- Run model inference for all samples (SLM/Claude baseline).
- Score and compare pre/post fine-tuning.