# UNICC Benchmark v1 全流程说明

本文档是当前项目 Benchmark 的单文件总说明，覆盖从数据准备到最终评分的完整流程。

适用目录：`benchmark_data/v1`

---

## 1. 目标与范围

Benchmark v1 用于评估以下四类目标：

- `e1`：Security / Adversarial
- `e2`：Governance / Compliance
- `e3`：UN Mission Fit
- `council`：端到端仲裁结果

核心目标：

1. 固化可复现评测数据集（gold）
2. 支持模型预测（predict）与 gold 对比评分
3. 支持后续 SLM 接入后的 pre/post 微调对比

---

## 2. 目录结构与核心文件

`benchmark_data/v1` 下主要文件：

- `raw/`：分来源候选数据
- `normalized/candidate_seed_all.jsonl`：候选全集
- `normalized/candidate_seed_clean.jsonl`：泄漏过滤后候选集
- `normalized/benchmark_final_v1.jsonl`：最终 gold 数据集（标注合并后）
- `splits/dev.jsonl`、`splits/test.jsonl`：开发/测试切分
- `manifests/`：schema、sources、标注模板、报告
- `predictions/`：预测模板、自动预测、待 SLM 队列
- `reports/`：评分报告、预检报告、队列摘要

---

## 3. 端到端流程概览

1. 生成候选集（seed）
2. 泄漏检查（leakage）
3. 导出标注模板
4. 人工标注 gold
5. 规范化标注（可选但推荐）
6. 合并生成 final benchmark
7. 预检（readiness gate）
8. 生成预测（模型输出）
9. 评分（score）
10. 准备 SLM 批跑队列（未接 SLM 时先排队）

---

## 4. 步骤与命令

以下命令均在项目根目录执行（`/Users/yangjunjie/Capstone`）。

### Step 1) 生成候选集

脚本：`benchmark_seed_builder.py`

```bash
python3 benchmark_seed_builder.py
```

输出：

- `benchmark_data/v1/raw/*`
- `benchmark_data/v1/normalized/candidate_seed_all.jsonl`
- `benchmark_data/v1/splits/dev.jsonl`
- `benchmark_data/v1/splits/test.jsonl`
- `benchmark_data/v1/manifests/seed_manifest_v1.json`

---

### Step 2) 泄漏检查（精确文本）

脚本：`benchmark_leakage_check.py`

```bash
python3 benchmark_leakage_check.py
```

输出：

- `benchmark_data/v1/normalized/candidate_seed_clean.jsonl`
- `benchmark_data/v1/normalized/candidate_seed_removed_by_leakage.jsonl`
- `benchmark_data/v1/manifests/leakage_report_v1.json`

说明：当前是 exact normalized 文本匹配；后续可加 semantic near-dup。

---

### Step 3) 导出标注模板

脚本：`benchmark_annotation_tools.py`

```bash
python3 benchmark_annotation_tools.py export-template
```

输出：

- `benchmark_data/v1/manifests/annotation_template_v1.csv`

---

### Step 4) 人工标注 gold（CSV）

主要字段：

- `gold_recommendation`：`APPROVE | REVIEW | REJECT`
- `gold_risk_tier`
- `gold_human_review_required`：`true/false`
- `gold_must_hit_findings`
- `gold_must_citations`（E2 重点）
- `gold_must_principles`（E3 重点）
- `annotator`
- `review_status`（建议填 `approved`）

分隔符规范：

- 多值字段用 `||`

---

### Step 5) 标注规范化（推荐）

脚本：`benchmark_annotation_normalize.py`

```bash
python3 benchmark_annotation_normalize.py \
  --in-csv "/path/to/annotation_template_v1_annotated.csv" \
  --out-csv "benchmark_data/v1/manifests/annotation_template_v1_annotated_cleaned.csv"
```

用途：

- 统一分隔符为 `||`
- 提升常见弱引用格式（例如 Annex 引用）
- 统一 `review_status`

---

### Step 6) 合并标注生成 final benchmark

脚本：`benchmark_annotation_tools.py`

```bash
python3 benchmark_annotation_tools.py apply-annotations \
  --csv "benchmark_data/v1/manifests/annotation_template_v1_annotated_cleaned.csv"
```

输出：

- `benchmark_data/v1/normalized/benchmark_final_v1.jsonl`
- `benchmark_data/v1/manifests/annotation_merge_report_v1.json`

---

### Step 7) 预检（是否可进入模型评测）

脚本：`benchmark_preflight.py`

```bash
python3 benchmark_preflight.py
```

输出：

- `benchmark_data/v1/reports/benchmark_readiness_v1.json`
- `benchmark_data/v1/reports/benchmark_readiness_v1.md`

目标状态：

- `status = READY_FOR_MODEL_BENCHMARKING`

---

### Step 8) 生成预测文件（predict）

#### 8.1 导出空模板

脚本：`benchmark_eval_runner.py`

```bash
python3 benchmark_eval_runner.py export-pred-template
```

输出：

- `benchmark_data/v1/predictions/predictions_template_v1.jsonl`

#### 8.2 自动填充（当前可用）

脚本：`benchmark_prediction_adapter.py`

```bash
python3 benchmark_prediction_adapter.py
```

输出：

- `benchmark_data/v1/predictions/predictions_autofill_v1.jsonl`
- `benchmark_data/v1/reports/predictions_autofill_summary_v1.json`

说明：自动填充会优先使用已有真实报告，其余样本用 heuristic fallback，仅用于流程验证，不代表最终模型能力。

---

### Step 9) 评分（score）

脚本：`benchmark_eval_runner.py`

```bash
python3 benchmark_eval_runner.py score \
  --pred "benchmark_data/v1/predictions/predictions_autofill_v1.jsonl"
```

输出：

- `benchmark_data/v1/reports/benchmark_eval_report_v1.json`
- `benchmark_data/v1/reports/benchmark_eval_report_v1.md`

指标包括：

- recommendation_accuracy
- human_review_accuracy
- must_hit_findings_coverage
- citation_coverage
- principle_coverage
- by_target 分解指标

---

### Step 10) SLM 未接入时先准备批跑队列

脚本：`benchmark_prepare_pending_slm.py`

```bash
python3 benchmark_prepare_pending_slm.py
```

输出：

- `benchmark_data/v1/predictions/pending_slm_queue_v1.jsonl`
- `benchmark_data/v1/reports/pending_slm_queue_summary_v1.json`

该队列按风险优先级排序（高风险优先）。

---

## 5. 当前 v1 状态定义

当前可分为三种状态：

1. **流程就绪**：数据、标注、评分链路可运行（当前已达到）
2. **模型评测就绪**：可跑真实模型输出并稳定出分（当前可做）
3. **对外报告就绪**：完成 pre/post 微调对比，结果可决策上线（SLM 接入后执行）

---

## 6. 常见问题

### Q1. 只填 `review_status` 行不行？

不行。至少还要有：

- `gold_recommendation`
- `gold_human_review_required`

建议再填 `must_hit_findings`（以及 E2/E3 对应字段），否则 coverage 指标无意义。

### Q2. `predict` 是什么？

`predict` 是模型输出答卷；`gold` 是人工标准答案。  
`score` 就是把两者对比打分。

### Q3. 为什么自动跑分低？

如果预测里使用了 heuristic fallback（非真实模型推理），分数只代表流程连通性，不代表真实模型能力。

---

## 7. 推荐下一步

1. 接入真实 SLM 推理（或先用 Claude 基线）
2. 跑完整 80 条预测，不用 fallback
3. 输出 pre-finetune vs post-finetune 对比报告
4. 基于阈值做 Go/No-Go 决策

