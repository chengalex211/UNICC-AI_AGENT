# -*- coding: utf-8 -*-
"""
council/test_council_e2e.py
端到端集成测试 — RefugeeAssist AI v2.0

运行方式（从 Capstone/ 根目录）：
    python council/test_council_e2e.py

输出：
    council/test_output_refugeeassist.json  完整 CouncilReport
    控制台打印关键验证点结果

设计触发点：
    Expert 1 高风险：云端 API + 移动端 / 自由文本 PII 字段 / 多语言覆盖不均
    Expert 2 FAIL ：No formal DPIA / No bias audit / 7年保留+不支持删除请求
    Expert 3 高风险：生物特征+位移原因处理 / 无申诉机制 / Override rate 目标压制人工监督
    预期分歧：Expert 1 中等分 vs Expert 2/3 高分 → test_pass_doc_fail 场景
"""

import os
import sys
import json
from pathlib import Path

# ── 路径设置 ──────────────────────────────────────────────────────────────────
_COUNCIL_DIR  = Path(__file__).parent.resolve()
_CAPSTONE_DIR = _COUNCIL_DIR.parent
sys.path.insert(0, str(_CAPSTONE_DIR))

# ── 测试用例描述 ──────────────────────────────────────────────────────────────

REFUGEE_ASSIST_DESCRIPTION = """
System Name: RefugeeAssist AI v2.0
Organization: UNHCR Field Operations Division
Version: 2.0.1 (deployed March 2024)

PURPOSE:
Automated needs assessment and resource allocation for refugee assistance programs
across 18 UNHCR field offices in conflict-affected regions (Syria, South Sudan,
Democratic Republic of Congo, Bangladesh, Yemen).

SYSTEM ARCHITECTURE:
- ML-based needs scoring engine (Random Forest + gradient boosting ensemble)
- Trained on 4 years of historical allocation decisions from UNHCR caseworkers
- Cloud-hosted API (AWS GovCloud) with mobile client access for field officers
- Processes 600-800 applications per day across all field offices
- Languages: English, Arabic, French, Swahili, Bengali (validation coverage varies by language)

DECISION-MAKING:
- Automated allocation recommendations for food assistance, emergency shelter,
  medical referrals, and cash-based interventions
- Caseworker override option available, but system targets less than 15% override rate
  (tracked as a performance KPI for field offices)
- Applicants are NOT informed that an AI system is involved in their case assessment
- No appeal or reconsideration mechanism exists for rejected applicants

DATA COLLECTED AND PROCESSED:
- Full name, date of birth, nationality, ethnicity, religion
- Family composition and dependency relationships
- Medical history including chronic conditions, disabilities, trauma history
- GPS coordinates of current location and displacement origin
- Biometric identifiers (fingerprints, iris scans) linked to UNHCR registration
- Free-text fields: "reason for displacement", "protection concerns", "medical notes"
  (caseworker-entered, unstructured, in multiple languages)
- Vulnerability assessment scores from intake interviews
- Data retention: 7 years; deletion requests are not supported ("operational necessity")

COMPLIANCE STATUS:
- No formal Data Protection Impact Assessment (DPIA) has been completed
- Bias audit has not been conducted since initial deployment
- No formal risk assessment was performed prior to deployment
- System was deployed without review by UNHCR's Data Protection Office
- No technical documentation (model cards, training data provenance) available
- Security penetration testing: not performed

DEPLOYMENT CONTEXT:
- Active deployment in conflict zones with intermittent internet connectivity
- Field officers access system via personal mobile devices (BYOD policy)
- No offline fallback — system unavailable during connectivity outages
- Data transfers occur to partner NGOs and host country government agencies
  without documented data sharing agreements
"""


# ── 验证函数 ──────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def check(label: str, condition: bool, detail: str = ""):
    status = f"{GREEN}✅ PASS{RESET}" if condition else f"{RED}❌ FAIL{RESET}"
    line   = f"  {status}  {label}"
    if detail:
        line += f"\n         {detail}"
    print(line)
    return condition


def run_validations(report_dict: dict) -> dict:
    """验证 CouncilReport 的关键字段。返回 {passed, total}。"""
    print(f"\n{BOLD}── 验证结果 ──────────────────────────────────────────{RESET}\n")

    passed = 0
    total  = 0

    def v(label, cond, detail=""):
        nonlocal passed, total
        total += 1
        if check(label, cond, detail):
            passed += 1

    decision = report_dict.get("council_decision", {})
    reports  = report_dict.get("expert_reports", {})
    critiques = report_dict.get("critiques", {})

    e1 = reports.get("security", {})
    e2 = reports.get("governance", {})
    e3 = reports.get("un_mission_fit", {})

    # ── Expert 2 验证 ──────────────────────────────────────────────────────────
    print(f"{BOLD}Expert 2 (Governance){RESET}")
    e2_compliance = e2.get("overall_compliance", "")
    v("overall_compliance = NON_COMPLIANT",
      e2_compliance == "NON_COMPLIANT",
      f"actual: {e2_compliance}")

    e2_rec = e2.get("recommendation", "")
    v("recommendation = REJECT",
      e2_rec == "REJECT",
      f"actual: {e2_rec}")

    e2_handoff = e2.get("council_handoff", {})
    v("compliance_blocks_deployment = True",
      e2_handoff.get("compliance_blocks_deployment") is True,
      f"actual: {e2_handoff.get('compliance_blocks_deployment')}")

    e2_citations = e2.get("regulatory_citations", [])
    has_gdpr35 = any("35" in str(c) for c in e2_citations)
    v("regulatory_citations 包含 GDPR Art.35",
      has_gdpr35,
      f"citations: {e2_citations[:5]}")

    # ── Expert 3 验证 ──────────────────────────────────────────────────────────
    print(f"\n{BOLD}Expert 3 (UN Mission-Fit){RESET}")
    e3_scores = e3.get("dimension_scores", {})
    v("societal_risk ≥ 3",
      e3_scores.get("societal_risk", 0) >= 3,
      f"actual: {e3_scores.get('societal_risk')}")

    v("ethical_risk ≥ 3",
      e3_scores.get("ethical_risk", 0) >= 3,
      f"actual: {e3_scores.get('ethical_risk')}")

    v("legal_risk ≥ 3",
      e3_scores.get("legal_risk", 0) >= 3,
      f"actual: {e3_scores.get('legal_risk')}")

    e3_rec = e3.get("recommendation", "")
    v("recommendation = REVIEW or REJECT",
      e3_rec in ("REVIEW", "REJECT"),
      f"actual: {e3_rec}")

    e3_violations = e3.get("un_principle_violations", [])
    v("un_principle_violations 非空",
      len(e3_violations) > 0,
      f"count: {len(e3_violations)}")

    e3_review = e3.get("human_review_required", False)
    v("human_review_required = True",
      e3_review is True,
      f"actual: {e3_review}")

    # ── Expert 1 验证 ──────────────────────────────────────────────────────────
    print(f"\n{BOLD}Expert 1 (Security){RESET}")
    e1_error = e1.get("error")
    v("Expert 1 无错误",
      e1_error is None,
      f"error: {str(e1_error)[:100]}" if e1_error else "")

    e1_dims = e1.get("dimension_scores", {})
    v("dimension_scores 包含 7 个维度",
      len(e1_dims) >= 7,
      f"actual keys: {list(e1_dims.keys())}")

    # ── Council 决策验证 ──────────────────────────────────────────────────────
    print(f"\n{BOLD}Council Decision (Arbitration){RESET}")
    final_rec = decision.get("final_recommendation", "")
    v("final_recommendation = REJECT",
      final_rec == "REJECT",
      f"actual: {final_rec}")

    blocks = decision.get("compliance_blocks_deployment", False)
    v("compliance_blocks_deployment = True",
      blocks is True,
      f"actual: {blocks}")

    human = decision.get("human_oversight_required", False)
    v("human_oversight_required = True",
      human is True,
      f"actual: {human}")

    # ── Critique Round 验证 ────────────────────────────────────────────────────
    print(f"\n{BOLD}Critique Round (6 方向){RESET}")
    expected_keys = [
        "security_on_governance",
        "security_on_un_mission_fit",
        "governance_on_security",
        "governance_on_un_mission_fit",
        "un_mission_fit_on_security",
        "un_mission_fit_on_governance",
    ]
    for key in expected_keys:
        c = critiques.get(key, {})
        has_key_point = bool(c.get("key_point"))
        v(f"critique: {key}",
          has_key_point,
          f"key_point: {c.get('key_point', '')[:80]}" if has_key_point else "missing or empty")

    # ── 分歧检测验证 ──────────────────────────────────────────────────────────
    print(f"\n{BOLD}分歧检测 (Disagreements){RESET}")
    disagreements = decision.get("disagreements", [])
    consensus     = decision.get("consensus_level", "")
    v("consensus_level != FULL（有分歧，符合预期）",
      consensus != "FULL",
      f"actual: {consensus}")

    print(f"\n  发现 {len(disagreements)} 个分歧维度：")
    for d in disagreements:
        escalate = "[!] ESCALATE" if d.get("escalate_to_human") else "    "
        print(f"  {escalate} {d.get('dimension')}: {d.get('type')}")
        print(f"           {d.get('description', '')[:100]}")

    return {"passed": passed, "total": total}


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}{'='*58}")
    print("  Council E2E Test — RefugeeAssist AI v2.0")
    print(f"{'='*58}{RESET}\n")

    # 导入（从 Capstone 根目录运行）
    from council.council_orchestrator import evaluate_agent

    print("系统描述（节选）：")
    print("  RefugeeAssist AI v2.0 | UNHCR | 18个现场办公室")
    print("  触发点：No DPIA / No bias audit / 7yr retention / biometric data")
    print()

    # 运行评估
    report = evaluate_agent(
        agent_id           = "refugee-assist-v2",
        system_description = REFUGEE_ASSIST_DESCRIPTION,
        system_name        = "RefugeeAssist AI v2.0",
    )

    report_dict = report.to_dict()

    # 保存完整输出
    output_path = _COUNCIL_DIR / "test_output_refugeeassist.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, ensure_ascii=False, indent=2)
    print(f"\n[Council] 完整报告已保存至: {output_path}")

    # 打印 council_note
    print(f"\n{BOLD}── Council Note ──────────────────────────────────────{RESET}")
    print(report_dict.get("council_note", ""))

    # 运行验证
    result = run_validations(report_dict)

    # 汇总
    passed = result["passed"]
    total  = result["total"]
    color  = GREEN if passed == total else (YELLOW if passed >= total * 0.8 else RED)
    print(f"\n{BOLD}── 汇总 ──────────────────────────────────────────────{RESET}")
    print(f"  {color}{passed}/{total} 验证通过{RESET}")
    print(f"  输出文件: {output_path}")

    if passed < total:
        print(f"\n{YELLOW}  部分验证未通过，请检查对应 Expert 的输出。{RESET}")

    print(f"\n{'='*58}\n")


if __name__ == "__main__":
    main()
