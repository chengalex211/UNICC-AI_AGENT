"""
Council Codebase Audit Script
运行方式：python check_codebase.py
会检查所有 Expert 和 Council 相关文件的存在性和关键字段
"""

import os
import json
import ast
import sys
from pathlib import Path

# ── 颜色输出 ──────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✅ {msg}{RESET}")
def err(msg):  print(f"  {RED}❌ {msg}{RESET}")
def warn(msg): print(f"  {YELLOW}⚠️  {msg}{RESET}")
def info(msg): print(f"  {BLUE}ℹ️  {msg}{RESET}")
def header(msg): print(f"\n{BOLD}{msg}{RESET}\n{'─'*50}")

# ── 配置：根据你的实际路径修改 ────────────────────────
BASE_PATHS_TO_TRY = [
    Path.cwd(),
    Path.home() / "Capstone",
    Path.home() / "capstone",
    Path.home() / "unicc",
    Path.home() / "Documents" / "Capstone",
]

EXPERT1_FILES = [
    "expert1_module.py",         # 实际入口文件名
    "generate_expert1_attack_data.py",
]

EXPERT2_FILES = [
    "expert2_agent.py",
]

EXPERT3_FILES = [
    "expert3_agent.py",
]

COUNCIL_FILES = [
    "council/__init__.py",
    "council/agent_submission.py",
    "council/critique_context.py",
    "council/critique.py",
    "council/council_report.py",
    "council/council_orchestrator.py",
]

# council_handoff 必须有的字段
REQUIRED_HANDOFF_FIELDS = [
    "privacy_score",
    "transparency_score",
    "bias_score",
    "human_oversight_required",
    "compliance_blocks_deployment",
    "note",
]

# ── 工具函数 ──────────────────────────────────────────
def find_base_path():
    """
    找到包含所有三个 Expert 子目录的项目根目录。
    优先找能同时覆盖 Expert 1/2/3 的最高层目录。
    """
    candidates = list(BASE_PATHS_TO_TRY)

    # 把脚本自身所在目录也加进去
    script_dir = Path(__file__).parent.resolve()
    if script_dir not in candidates:
        candidates.insert(0, script_dir)

    for p in candidates:
        if not p.exists():
            continue
        # 只有能同时找到 Expert 2 和 Expert 3（或 Expert 1）的目录才是根
        subdirs = [s.name for s in p.iterdir() if s.is_dir()]
        has_e2 = any("expert 2" in s.lower() or s.lower() == "expert2" for s in subdirs)
        has_e3 = any("expert 3" in s.lower() or s.lower() == "expert3" for s in subdirs)
        has_e1 = any("expert 1" in s.lower() or s.lower() == "expert1"
                     or "unicc-ai-agent" in s.lower() for s in subdirs)
        if has_e2 and (has_e3 or has_e1):
            return p

    return script_dir

def check_file_exists(base: Path, filename: str) -> bool:
    return (base / filename).exists()

def extract_python_strings(filepath: Path) -> str:
    """读取文件内容"""
    try:
        return filepath.read_text(encoding="utf-8")
    except Exception:
        return ""

def check_handoff_fields(content: str, expert_name: str):
    """检查 council_handoff 是否包含所有必要字段"""
    if "council_handoff" not in content:
        err(f"{expert_name}: 没有找到 council_handoff")
        return False
    
    missing = []
    for field in REQUIRED_HANDOFF_FIELDS:
        if field not in content:
            missing.append(field)
    
    if missing:
        warn(f"{expert_name} council_handoff 缺少字段: {missing}")
        return False
    else:
        ok(f"{expert_name}: council_handoff 字段完整")
        return True

def check_recommendation_values(content: str, expert_name: str):
    """检查 recommendation 的值是否规范"""
    valid = ["APPROVE", "REVIEW", "REJECT"]
    found = [v for v in valid if v in content]
    if found:
        ok(f"{expert_name}: recommendation 包含 {found}")
    else:
        warn(f"{expert_name}: 未找到标准 recommendation 值 (APPROVE/REVIEW/REJECT)")

def check_risk_tier(content: str, expert_name: str):
    """检查 risk_tier 定义"""
    tiers_e1 = ["MINIMAL", "LIMITED", "SIGNIFICANT", "UNACCEPTABLE"]
    tiers_e3 = ["MINIMAL", "LIMITED", "HIGH", "UNACCEPTABLE"]
    
    found_e1 = all(t in content for t in tiers_e1)
    found_e3 = all(t in content for t in tiers_e3)
    
    if found_e1:
        ok(f"{expert_name}: risk_tier 使用 E1 标准 (MINIMAL/LIMITED/SIGNIFICANT/UNACCEPTABLE)")
    elif found_e3:
        ok(f"{expert_name}: risk_tier 使用 E3 标准 (MINIMAL/LIMITED/HIGH/UNACCEPTABLE)")
    else:
        warn(f"{expert_name}: risk_tier 定义不完整或使用非标准值")

def check_chromadb(content: str, expert_name: str):
    """检查 ChromaDB 配置"""
    if "chromadb" in content.lower() or "chroma" in content.lower():
        ok(f"{expert_name}: 使用 ChromaDB")
        if "collection_name" in content:
            # 提取 collection name
            import re
            match = re.search(r'collection_name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                info(f"{expert_name}: collection = '{match.group(1)}'")
    else:
        warn(f"{expert_name}: 未找到 ChromaDB 配置")

def check_compliance_conversion(content: str):
    """检查 Expert 2 是否有 PASS/FAIL → 数字 的转换逻辑"""
    has_rule_conversion = any(kw in content for kw in [
        "COMPLIANCE_TO_SCORE", "compliance_to_score",
        "FAIL.*4", "PASS.*1",
        "to_score", "score_map"
    ])
    has_claude_scoring = "直接评分" in content or "direct score" in content.lower()
    
    if has_rule_conversion:
        ok("Expert 2: PASS/FAIL→数字 使用规则转换 ✓")
    elif has_claude_scoring:
        warn("Expert 2: council_handoff 数字依赖模型评分，建议改成规则转换")
    else:
        warn("Expert 2: 未找到明确的 PASS/FAIL→数字 转换逻辑，需要确认")

def count_training_samples(base: Path, expert_name: str, patterns: list):
    """统计训练数据样本数"""
    total = 0
    found_files = []
    
    for pattern in patterns:
        files = list(base.rglob(pattern))
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                # 尝试解析 JSON Lines
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                json_count = 0
                for line in lines:
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            json_count += 1
                    except:
                        pass
                
                # 尝试解析 JSON Array
                if json_count == 0:
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            json_count = len(data)
                    except:
                        pass
                
                if json_count > 0:
                    total += json_count
                    found_files.append((f.name, json_count))
            except:
                pass
    
    if total > 0:
        ok(f"{expert_name}: 找到 {total} 条训练样本")
        for fname, count in found_files:
            info(f"  {fname}: {count} 条")
    else:
        warn(f"{expert_name}: 未找到训练数据文件，检查路径")
    
    return total

def check_imports(content: str, expert_name: str):
    """检查关键 import"""
    key_imports = {
        "anthropic": "Anthropic SDK",
        "chromadb":  "ChromaDB",
        "dataclass": "dataclass",
    }
    for imp, name in key_imports.items():
        if imp in content:
            ok(f"{expert_name}: 使用 {name}")

# ── 主检查逻辑 ────────────────────────────────────────
def main():
    print(f"\n{BOLD}{'='*50}")
    print("  Council Codebase Audit")
    print(f"{'='*50}{RESET}")
    
    # 找项目根目录
    base = find_base_path()
    print(f"\n📁 检查路径: {base}")
    
    results = {
        "expert1": False,
        "expert2": False,
        "expert3": False,
        "council": False,
        "training_data": {},
        "handoff_complete": {},
    }

    # ── Expert 1 ──────────────────────────────────────
    header("Expert 1：Security & Adversarial Testing")
    
    e1_path = None
    e1_dirs = (
        [base / d for d in os.listdir(base)
         if os.path.isdir(base / d) and
         ("expert 1" in d.lower() or d.lower() in ("expert1",) or "unicc-ai-agent" in d.lower())]
        + [base]
    )
    for fname in EXPERT1_FILES:
        found = False
        for search_base in e1_dirs:
            if (search_base / fname).exists():
                ok(f"找到 {fname}")
                e1_path = search_base / fname
                found = True
                break
        if not found:
            err(f"缺少 {fname}")
    
    if e1_path and e1_path.exists():
        content = extract_python_strings(e1_path)
        check_handoff_fields(content, "Expert 1")
        check_recommendation_values(content, "Expert 1")
        check_risk_tier(content, "Expert 1")
        check_chromadb(content, "Expert 1")
        results["expert1"] = True
    
    e1_data_base = e1_dirs[0] if e1_dirs and e1_dirs[0] != base else base
    e1_samples = count_training_samples(
        e1_data_base, "Expert 1",
        ["*expert1*training*.json*", "*expert1*data*.json*", "*attack*data*.json*"]
    )
    results["training_data"]["expert1"] = e1_samples

    # ── Expert 2 ──────────────────────────────────────
    header("Expert 2：Governance & Compliance")
    
    e2_path = None
    e2_dirs = (
        [base / d for d in os.listdir(base)
         if os.path.isdir(base / d) and
         ("expert 2" in d.lower() or d.lower() in ("expert2",) or
          "unicc-ai-safety-sandbox" in d.lower())]
        + [base]
    )
    for fname in EXPERT2_FILES:
        found = False
        for search_base in e2_dirs:
            if (search_base / fname).exists():
                ok(f"找到 {fname}")
                e2_path = search_base / fname
                found = True
                break
        if not found:
            err(f"缺少 {fname}")
    
    if e2_path and e2_path.exists():
        content = extract_python_strings(e2_path)
        check_handoff_fields(content, "Expert 2")
        check_compliance_conversion(content)
        check_recommendation_values(content, "Expert 2")
        check_chromadb(content, "Expert 2")
        results["expert2"] = True
    
    e2_data_base = e2_dirs[0] if e2_dirs and e2_dirs[0] != base else base
    e2_samples = count_training_samples(
        e2_data_base, "Expert 2",
        ["*expert2*training*.json*", "*expert2*data*.json*", "*compliance*data*.json*"]
    )
    results["training_data"]["expert2"] = e2_samples

    # ── Expert 3 ──────────────────────────────────────
    header("Expert 3：UN Mission-Fit")
    
    e3_path = None
    e3_dirs = (
        [base / d for d in os.listdir(base)
         if os.path.isdir(base / d) and
         ("expert 3" in d.lower() or d.lower() in ("expert3",))]
        + [base]
    )
    for fname in EXPERT3_FILES:
        found = False
        for search_base in e3_dirs:
            if (search_base / fname).exists():
                ok(f"找到 {fname}")
                e3_path = search_base / fname
                found = True
                break
        if not found:
            err(f"缺少 {fname}")
    
    if e3_path and e3_path.exists():
        content = extract_python_strings(e3_path)
        check_handoff_fields(content, "Expert 3")
        check_recommendation_values(content, "Expert 3")
        check_risk_tier(content, "Expert 3")
        check_chromadb(content, "Expert 3")
        
        # Expert 3 特有字段
        special_fields = ["un_principle_violations", "human_review_required", "tier_mismatch_corrected"]
        for field in special_fields:
            if field in content:
                ok(f"Expert 3: 包含 {field}")
            else:
                warn(f"Expert 3: 缺少 {field}")
        
        results["expert3"] = True
    
    e3_data_base = e3_dirs[0] if e3_dirs and e3_dirs[0] != base else base
    e3_samples = count_training_samples(
        e3_data_base, "Expert 3",
        ["*expert3*training*.json*", "*expert3*data*.json*", "*un*mission*.json*"]
    )
    results["training_data"]["expert3"] = e3_samples

    # ── Council 层 ────────────────────────────────────
    header("Council：Orchestrator 层")
    
    council_exists = 0
    for fname in COUNCIL_FILES:
        if check_file_exists(base, fname):
            ok(f"找到 {fname}")
            council_exists += 1
        else:
            err(f"缺少 {fname}  ← 需要新建")
    
    results["council"] = council_exists > 0

    # ── Critique 训练数据 ─────────────────────────────
    header("Critique 训练数据")
    
    critique_samples = count_training_samples(
        base, "Critique",
        ["*critique*training*.json*", "*critique*data*.json*"]
    )
    results["training_data"]["critique"] = critique_samples
    
    if critique_samples == 0:
        warn("Critique 训练数据：0条（需要生成，优先级高）")

    # ── 汇总报告 ──────────────────────────────────────
    header("汇总报告")
    
    print(f"\n{'组件':<25} {'状态':<15} {'训练数据'}")
    print("─" * 55)
    
    def status(ok): return f"{GREEN}✅ 存在{RESET}" if ok else f"{RED}❌ 缺失{RESET}"
    def data_status(n, threshold):
        if n >= threshold:
            return f"{GREEN}{n}条 ✅{RESET}"
        elif n > 0:
            return f"{YELLOW}{n}条 ⚠️{RESET}"
        else:
            return f"{RED}0条 ❌{RESET}"
    
    print(f"{'Expert 1 (Security)':<25} {status(results['expert1']):<24} {data_status(results['training_data'].get('expert1',0), 200)}")
    print(f"{'Expert 2 (Governance)':<25} {status(results['expert2']):<24} {data_status(results['training_data'].get('expert2',0), 100)}")
    print(f"{'Expert 3 (UN Mission)':<25} {status(results['expert3']):<24} {data_status(results['training_data'].get('expert3',0), 120)}")
    print(f"{'Council Orchestrator':<25} {status(results['council']):<24} {'N/A'}")
    print(f"{'Critique Round':<25} {'─':<15} {data_status(results['training_data'].get('critique',0), 300)}")
    
    print(f"\n{BOLD}立即需要做的事：{RESET}")
    
    todos = []
    if not results["expert1"]: todos.append("找到 Expert 1 代码文件")
    if not results["expert2"]: todos.append("找到 Expert 2 代码文件")
    if not results["expert3"]: todos.append("找到 Expert 3 代码文件")
    if not results["council"]: todos.append("创建 council/ 目录和所有文件（从零开始）")
    if results["training_data"].get("expert2", 0) < 100:
        todos.append(f"Expert 2 训练数据补充到100+条（现在{results['training_data'].get('expert2',0)}条）")
    if results["training_data"].get("critique", 0) == 0:
        todos.append("生成 Critique 训练数据（目标300条，优先级最高）")
    
    for i, todo in enumerate(todos, 1):
        print(f"  {i}. {todo}")
    
    if not todos:
        print(f"  {GREEN}所有组件齐全！可以开始集成测试。{RESET}")
    
    print(f"\n{'='*50}\n")

if __name__ == "__main__":
    main()
