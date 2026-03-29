# Benchmark Sources v1

Locked source list for benchmark seed generation:

- E1 incident seeds: `Expert1/incidents.csv`
- E1 attack taxonomy seeds: `atlas-data/dist/ATLAS.yaml`
- E2 compliance seeds: `council/results/summary.json`
- E3 mission-fit seeds: `Expert 3/expert3_training_data/aiid_selected_incidents.csv`
- Council seeds: `council/results/summary.json` + `council/results/reports/*.json`

Rules:

1. Seed rows are not final benchmark gold labels.
2. Manual annotation is required for `must_hit_findings` and final recommendations.
3. Run leakage checks before benchmark promotion.

