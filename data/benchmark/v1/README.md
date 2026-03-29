# Benchmark v1 Seed Pack

This folder contains the first benchmark seed pack generated with a semi-automatic pipeline.

## Generated Files

- `raw/candidate_seed_e1_incidents.jsonl`
- `raw/candidate_seed_e1_atlas.jsonl`
- `raw/candidate_seed_e2.jsonl`
- `raw/candidate_seed_e3.jsonl`
- `raw/candidate_seed_council.jsonl`
- `normalized/candidate_seed_all.jsonl`
- `splits/dev.jsonl`
- `splits/test.jsonl`
- `manifests/seed_manifest_v1.json`
- `manifests/benchmark_schema_v1.json`
- `manifests/benchmark_sources_v1.md`

## Important

This is a **seed pack**, not final benchmark gold.

Rows tagged with:
- `needs_gold`: manual annotation required
- `needs_dedup`: overlap/leakage checks required against training corpora

## Build Command

```bash
python3 benchmark_seed_builder.py
```

## Recommended Next Steps

1. Human annotation pass on `provisional_gold`.
2. Run strict de-duplication against all training JSONL files.
3. Promote validated rows into `benchmark_final_v1`.

