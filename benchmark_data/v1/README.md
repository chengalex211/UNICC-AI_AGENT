# Benchmark Data v1

This folder contains benchmark candidate data generated for all experts (E1/E2/E3/Council).

## How to regenerate

```bash
python3 benchmark_seed_builder.py
python3 benchmark_leakage_check.py
python3 benchmark_annotation_tools.py export-template
```

## Structure

- `raw/` source-specific candidate pools
- `normalized/` merged candidate sets
- `splits/` dev/test splits
- `manifests/` build metadata and quality reports

## Current status

- `candidate_seed_all.jsonl`: raw merged candidates
- `candidate_seed_clean.jsonl`: exact-overlap leakage filtered candidates
- `seed_manifest_v1.json`: generation summary
- `leakage_report_v1.json`: overlap check summary
- `annotation_template_v1.csv`: manual labeling template
- `annotation_guide_v1.md`: annotation instructions

> Note: This is still a seed pack. Manual gold annotation is required before final benchmark promotion.

## Annotation merge

After filling annotation CSV:

```bash
python3 benchmark_annotation_tools.py apply-annotations
```

This produces:
- `benchmark_data/v1/normalized/benchmark_final_v1.jsonl`
- `benchmark_data/v1/manifests/annotation_merge_report_v1.json`

## Evaluation pipeline

Export prediction template:

```bash
python3 benchmark_eval_runner.py export-pred-template
```

Run scoring:

```bash
python3 benchmark_eval_runner.py score
```

Outputs:
- `benchmark_data/v1/reports/benchmark_eval_report_v1.json`
- `benchmark_data/v1/reports/benchmark_eval_report_v1.md`
