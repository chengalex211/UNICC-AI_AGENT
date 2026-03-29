# -*- coding: utf-8 -*-
"""
run_batch_eval.py
批量运行所有测试案例，生成 CouncilReport，保存结果。

用法：
    python run_batch_eval.py
    python run_batch_eval.py --start 0 --end 10      # 只跑前10个
    python run_batch_eval.py --case-id supply-chain-ai-v2  # 跑单个案例

输出：
    results/reports/{agent_id}.json   每个案例的完整 CouncilReport
    results/summary.json              所有案例的汇总表
    results/summary.csv               汇总表 CSV 版（方便查看）
"""

import sys
import os
import json
import csv
import argparse
import time
import traceback
from datetime import datetime
from pathlib import Path

# 把上级目录加入 path，确保 council 模块可以找到
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_cases_all import TEST_CASES

# 输出目录
RESULTS_DIR = Path(__file__).parent / "results"
REPORTS_DIR = RESULTS_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════
# 导入 Council 入口
# ══════════════════════════════════════════════════════════════════════

def load_evaluate_agent():
    """延迟导入，避免启动时报错。"""
    try:
        from council import evaluate_agent
        return evaluate_agent
    except ImportError as e:
        print(f"[ERROR] 无法导入 council.evaluate_agent: {e}")
        print("       请确认 council/__init__.py 已正确配置。")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════
# 单案例运行
# ══════════════════════════════════════════════════════════════════════

def run_single_case(case: dict, evaluate_agent) -> dict:
    """
    运行单个案例，返回结果记录。
    不抛异常，所有错误记录在结果里。
    """
    agent_id = case["agent_id"]
    system_name = case["system_name"]
    expected = case["expected"]

    print(f"\n{'─'*60}")
    print(f"[{agent_id}] {system_name}")
    print(f"  预期: E1={expected['e1']} E2={expected['e2']} E3={expected['e3']} Pattern={expected['pattern']}")

    start_time = time.time()
    error = None
    report = None

    try:
        report = evaluate_agent(
            agent_id=agent_id,
            system_description=case["system_description"],
            system_name=system_name,
        )
    except Exception as e:
        error = str(e)
        print(f"  [ERROR] {e}")
        traceback.print_exc()

    elapsed = round(time.time() - start_time, 1)

    # 提取实际结果
    actual_e1 = actual_e2 = actual_e3 = "ERROR"
    actual_decision = consensus = "ERROR"
    disagreement_count = 0

    if report and not error:
        try:
            # CouncilReport 可能是 dict 或 dataclass，统一转 dict
            if hasattr(report, "to_dict"):
                report_dict = report.to_dict()
            elif isinstance(report, dict):
                report_dict = report
            else:
                report_dict = vars(report)

            # 提取三位专家建议
            expert_reports = report_dict.get("expert_reports", {})
            actual_e1 = _extract_recommendation(expert_reports.get("security", {}))
            actual_e2 = _extract_recommendation(expert_reports.get("governance", {}))
            actual_e3 = _extract_recommendation(expert_reports.get("un_mission_fit", {}))

            # 提取 Council 决策
            council = report_dict.get("council_decision", {})
            actual_decision = council.get("final_recommendation", "UNKNOWN")
            consensus = council.get("consensus_level", "UNKNOWN")
            disagreements = report_dict.get("disagreements", [])
            disagreement_count = len(disagreements) if disagreements else 0

            # 保存完整报告
            report_path = REPORTS_DIR / f"{agent_id}.json"
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_dict, f, ensure_ascii=False, indent=2, default=str)

            print(f"  实际: E1={actual_e1} E2={actual_e2} E3={actual_e3}")
            print(f"  决策: {actual_decision} | 共识: {consensus} | 分歧数: {disagreement_count}")
            print(f"  耗时: {elapsed}s")

        except Exception as e:
            error = f"结果解析失败: {e}"
            print(f"  [PARSE ERROR] {e}")

    # 判断是否符合预期
    e1_match = actual_e1 == expected["e1"]
    e2_match = actual_e2 == expected["e2"]
    e3_match = actual_e3 == expected["e3"]
    all_match = e1_match and e2_match and e3_match

    if all_match:
        print(f"  ✅ 三方建议符合预期")
    else:
        mismatches = []
        if not e1_match: mismatches.append(f"E1预期{expected['e1']}实际{actual_e1}")
        if not e2_match: mismatches.append(f"E2预期{expected['e2']}实际{actual_e2}")
        if not e3_match: mismatches.append(f"E3预期{expected['e3']}实际{actual_e3}")
        print(f"  ⚠️  不符合预期: {', '.join(mismatches)}")

    return {
        "agent_id":          agent_id,
        "system_name":       system_name,
        "source":            case.get("source", "unknown"),
        "pattern":           expected["pattern"],
        "expected_e1":       expected["e1"],
        "expected_e2":       expected["e2"],
        "expected_e3":       expected["e3"],
        "actual_e1":         actual_e1,
        "actual_e2":         actual_e2,
        "actual_e3":         actual_e3,
        "actual_decision":   actual_decision,
        "consensus":         consensus,
        "disagreement_count": disagreement_count,
        "e1_match":          e1_match,
        "e2_match":          e2_match,
        "e3_match":          e3_match,
        "all_match":         all_match,
        "elapsed_seconds":   elapsed,
        "error":             error,
    }


def _extract_recommendation(expert_report: dict) -> str:
    """从 Expert 报告 dict 里提取 recommendation 字段。"""
    if not expert_report:
        return "MISSING"
    # 直接字段
    if "recommendation" in expert_report:
        return str(expert_report["recommendation"]).upper()
    # council_handoff 里
    handoff = expert_report.get("council_handoff", {})
    if handoff:
        rec = handoff.get("compliance_blocks_deployment")
        if rec is True:
            return "REJECT"
    return "UNKNOWN"


# ══════════════════════════════════════════════════════════════════════
# 批量运行
# ══════════════════════════════════════════════════════════════════════

def run_batch(cases: list, evaluate_agent) -> list:
    results = []
    total = len(cases)

    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/{total}] 运行中...")
        result = run_single_case(case, evaluate_agent)
        results.append(result)

        # 每10个案例自动保存一次，防止中途失败丢数据
        if i % 10 == 0:
            _save_results(results)
            print(f"\n  [已自动保存 {i}/{total} 条结果]")

    return results


def _save_results(results: list):
    """保存汇总结果到 JSON 和 CSV。"""
    # JSON
    summary_path = RESULTS_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total": len(results),
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    # CSV
    if results:
        csv_path = RESULTS_DIR / "summary.csv"
        fieldnames = list(results[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


def print_summary(results: list):
    """打印运行结束后的汇总统计。"""
    total = len(results)
    errors = sum(1 for r in results if r["error"])
    all_match = sum(1 for r in results if r["all_match"])
    e1_match = sum(1 for r in results if r["e1_match"])
    e2_match = sum(1 for r in results if r["e2_match"])
    e3_match = sum(1 for r in results if r["e3_match"])

    print(f"\n{'═'*60}")
    print(f"批量运行完成")
    print(f"{'═'*60}")
    print(f"总案例数:     {total}")
    print(f"运行错误:     {errors}")
    print(f"三方全符合:   {all_match}/{total} ({100*all_match//total}%)")
    print(f"E1 符合率:    {e1_match}/{total}")
    print(f"E2 符合率:    {e2_match}/{total}")
    print(f"E3 符合率:    {e3_match}/{total}")

    # 不符合预期的案例列表
    mismatches = [r for r in results if not r["all_match"] and not r["error"]]
    if mismatches:
        print(f"\n⚠️  不符合预期的案例 ({len(mismatches)}个):")
        for r in mismatches:
            parts = []
            if not r["e1_match"]: parts.append(f"E1:{r['expected_e1']}→{r['actual_e1']}")
            if not r["e2_match"]: parts.append(f"E2:{r['expected_e2']}→{r['actual_e2']}")
            if not r["e3_match"]: parts.append(f"E3:{r['expected_e3']}→{r['actual_e3']}")
            print(f"  {r['agent_id']:<35} {', '.join(parts)}")

    if errors > 0:
        print(f"\n❌ 运行出错的案例 ({errors}个):")
        for r in results:
            if r["error"]:
                print(f"  {r['agent_id']:<35} {r['error'][:80]}")

    print(f"\n结果已保存:")
    print(f"  {RESULTS_DIR}/summary.json")
    print(f"  {RESULTS_DIR}/summary.csv")
    print(f"  {REPORTS_DIR}/*.json  (每个案例的完整报告)")


# ══════════════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="批量运行 Council 评估")
    parser.add_argument("--start",   type=int, default=0,    help="起始索引（含）")
    parser.add_argument("--end",     type=int, default=None, help="结束索引（不含），默认全部")
    parser.add_argument("--case-id", type=str, default=None, help="只跑指定 agent_id 的案例")
    args = parser.parse_args()

    evaluate_agent = load_evaluate_agent()

    # 筛选案例
    if args.case_id:
        cases = [c for c in TEST_CASES if c["agent_id"] == args.case_id]
        if not cases:
            print(f"[ERROR] 找不到 agent_id={args.case_id}")
            print("可用的 agent_id:")
            for c in TEST_CASES:
                print(f"  {c['agent_id']}")
            sys.exit(1)
    else:
        end = args.end or len(TEST_CASES)
        cases = TEST_CASES[args.start:end]

    print(f"准备运行 {len(cases)} 个案例")
    print(f"结果保存到: {RESULTS_DIR}")

    results = run_batch(cases, evaluate_agent)
    _save_results(results)
    print_summary(results)


if __name__ == "__main__":
    main()
