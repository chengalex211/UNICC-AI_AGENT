# Benchmark Sources v1

This file defines the locked source set for benchmark seed generation.

## Core Sources

- E1 incident seeds: `Expert1/incidents.csv`
- E1 attack taxonomy seeds: `atlas-data/dist/ATLAS.yaml`
- E2 seeds: `Expert 2/expert2_training_data_clean.jsonl`
- E3 seeds: `Expert 3/expert3_training_data/training_data_expert3_final_fixed.jsonl`
- Council seeds: `council/results/summary.json` + `council/test_cases_all.py`

## Important Rules

- Seeds are **not final benchmark gold labels**.
- Any row tagged with `needs_gold` must be manually annotated.
- Any row tagged with `needs_dedup` must pass overlap checks against training sets.
- Final benchmark promotion requires:
  - label validation,
  - leakage checks,
  - expert review sign-off.

## Versioning

- Version: `v1`
- Build script: `benchmark_seed_builder.py`
- Random seed: `42`

