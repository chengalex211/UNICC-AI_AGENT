"""
rag/convert_atlas_to_md.py
Expert 1 RAG — ATLAS.yaml → Markdown Converter

将 MITRE ATLAS.yaml 转换为两个 knowledge_base 文件：
  1. knowledge_base/attack_techniques/ATLAS_Techniques.md
     每个技术 = 一个 ## 章节，共约 155 条

  2. knowledge_base/attack_strategies/ATLAS_Case_Studies.md
     每个案例 = 一个 ## 章节，共约 52 条

运行一次即可，输出结果提交到 git（不依赖 DGX）。

Usage:
    python rag/convert_atlas_to_md.py
    python rag/convert_atlas_to_md.py --atlas-path ../../atlas-data/dist/ATLAS.yaml
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

# ─── 默认路径 ─────────────────────────────────────────────────────────────────
# Expert 1 目录 → ../../atlas-data/dist/ATLAS.yaml
DEFAULT_ATLAS_PATH = Path(__file__).parent.parent.parent / "atlas-data" / "dist" / "ATLAS.yaml"
OUTPUT_TECHNIQUES  = Path(__file__).parent.parent / "knowledge_base" / "attack_techniques" / "ATLAS_Techniques.md"
OUTPUT_CASESTUDIES = Path(__file__).parent.parent / "knowledge_base" / "attack_strategies" / "ATLAS_Case_Studies.md"

# ─── LLM/Agent 공격에 관련된 전술 필터 ────────────────────────────────────────
# 仅保留与 LLM/AI Agent 攻击相关的战术
RELEVANT_TACTIC_IDS = {
    "AML.TA0000",  # Reconnaissance
    "AML.TA0001",  # Resource Development
    "AML.TA0002",  # Initial Access
    "AML.TA0004",  # Execution
    "AML.TA0005",  # Persistence
    "AML.TA0006",  # Defense Evasion
    "AML.TA0007",  # Discovery
    "AML.TA0008",  # Collection
    "AML.TA0009",  # Exfiltration
    "AML.TA0040",  # Impact
    "AML.TA0043",  # ML Model Access
    "AML.TA0044",  # Reconnaissance (extended)
}


def load_atlas(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def slugify_id(raw_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", raw_id)


# ─── TECHNIQUES → MARKDOWN ────────────────────────────────────────────────────

def extract_techniques(atlas: dict) -> list[dict]:
    # ATLAS.yaml 结构：techniques 在 matrices[0]["techniques"] 里
    raw = atlas.get("techniques", [])
    if not raw and atlas.get("matrices"):
        raw = atlas["matrices"][0].get("techniques", [])

    techniques = []
    for obj in raw:
        obj_id = obj.get("id", "")
        name   = obj.get("name", "")
        desc   = (obj.get("description", "") or "").strip()
        # tactics 字段可能是字符串列表或 dict 列表
        raw_tactics = obj.get("tactics", [])
        tactics = [
            t if isinstance(t, str) else t.get("id", "")
            for t in raw_tactics
        ]

        # 跳过与 LLM 攻击无关的战术
        if RELEVANT_TACTIC_IDS and not any(t in RELEVANT_TACTIC_IDS for t in tactics):
            continue

        techniques.append({
            "id":          obj_id,
            "name":        name,
            "description": desc,
            "tactics":     tactics,
            "subtechniques": [
                sub.get("id", "") for sub in obj.get("subtechniques", [])
            ] if "subtechniques" in obj else [],
            "platforms":   obj.get("platforms", []),
        })
    return techniques


def techniques_to_md(techniques: list[dict]) -> str:
    lines = [
        "# ATLAS Attack Techniques",
        "**Source:** MITRE ATLAS (Adversarial Threat Landscape for AI Systems)",
        "**Filtered:** LLM / AI Agent relevant tactics only",
        f"**Count:** {len(techniques)} techniques",
        "",
        "---",
        "",
    ]

    # 攻击层映射（用于 RAG 标签）
    application_ids = {"AML.T0054", "AML.T0051", "AML.T0056", "AML.T0057"}
    model_ids       = {"AML.T0001", "AML.T0005", "AML.T0006", "AML.T0015"}

    for t in techniques:
        tid   = t["id"]
        name  = t["name"]
        desc  = t["description"] or "No description available."
        tactics_str = ", ".join(t["tactics"]) if t["tactics"] else "N/A"

        # 推断攻击层
        if tid in application_ids or "prompt" in name.lower() or "injection" in name.lower():
            layer = "application"
        elif tid in model_ids or "model" in name.lower() or "training" in name.lower():
            layer = "model"
        else:
            layer = "social_engineering"

        lines += [
            f"## {tid} — {name}",
            "",
            f"**Tactics:** {tactics_str}  ",
            f"**Attack Layer:** {layer}  ",
            f"**ID:** `{tid}`  ",
            "",
            desc,
            "",
        ]

        if t["subtechniques"]:
            lines.append(f"**Subtechniques:** {', '.join(t['subtechniques'])}")
            lines.append("")

        if t["platforms"]:
            lines.append(f"**Platforms:** {', '.join(str(p) for p in t['platforms'])}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # RAG 检索标签
    all_names = " ".join(t["name"].lower() for t in techniques)
    lines += [
        "## RAG Retrieval Tags",
        "",
        "`ATLAS`, `attack_technique`, `adversarial_ml`, `LLM_attack`,",
        "`prompt_injection`, `model_extraction`, `evasion`, `poisoning`,",
        "`social_engineering`, `red_team`, `security_vulnerability`",
        "",
    ]
    return "\n".join(lines)


# ─── CASE STUDIES → MARKDOWN ──────────────────────────────────────────────────

def extract_case_studies(atlas: dict) -> list[dict]:
    return atlas.get("case-studies", atlas.get("case_studies", []))


def case_studies_to_md(case_studies: list[dict]) -> str:
    lines = [
        "# ATLAS Attack Case Studies",
        "**Source:** MITRE ATLAS — Real-World AI Attack Incidents",
        f"**Count:** {len(case_studies)} case studies",
        "",
        "---",
        "",
    ]

    for cs in case_studies:
        cs_id   = cs.get("id", "UNKNOWN")
        name    = cs.get("name", "Unnamed Case Study")
        summary = (cs.get("summary", cs.get("description", "")) or "").strip()

        # 使用的技术
        procedures = cs.get("procedure", cs.get("procedures", []))
        techs_used = []
        procedure_text_parts = []
        for proc in (procedures or []):
            tech_id   = proc.get("technique", {}).get("id", "") if isinstance(proc.get("technique"), dict) else proc.get("technique", "")
            tech_name = proc.get("technique", {}).get("name", "") if isinstance(proc.get("technique"), dict) else ""
            desc      = (proc.get("description", "") or "").strip()
            if tech_id:
                techs_used.append(tech_id)
            if desc:
                procedure_text_parts.append(f"- [{tech_id}] {desc}")

        techs_str = ", ".join(techs_used) if techs_used else "Not specified"
        procedure_text = "\n".join(procedure_text_parts) if procedure_text_parts else "See original ATLAS entry."

        # 推断 humanitarian 相关性
        combined_text = (name + " " + summary).lower()
        if any(kw in combined_text for kw in ["healthcare", "medical", "government", "financial", "military", "autonomous"]):
            relevance = "high"
        else:
            relevance = "medium"

        lines += [
            f"## {cs_id} — {name}",
            "",
            f"**Techniques Used:** {techs_str}  ",
            f"**Humanitarian Relevance:** {relevance}  ",
            "",
            "**Summary:**",
            summary or "No summary available.",
            "",
            "**Attack Procedure:**",
            procedure_text,
            "",
            "---",
            "",
        ]

    lines += [
        "## RAG Retrieval Tags",
        "",
        "`ATLAS_case_study`, `real_world_attack`, `AI_incident`,",
        "`attack_scenario`, `vulnerability_exploitation`, `red_team_reference`,",
        "`humanitarian_risk`, `case_study`",
        "",
    ]
    return "\n".join(lines)


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Convert ATLAS.yaml to markdown")
    parser.add_argument("--atlas-path", type=Path, default=DEFAULT_ATLAS_PATH)
    args = parser.parse_args()

    atlas_path = args.atlas_path
    if not atlas_path.exists():
        print(f"ERROR: ATLAS.yaml not found at {atlas_path}")
        print("Run: git clone --depth 1 -b main https://github.com/mitre-atlas/atlas-data atlas-data")
        sys.exit(1)

    print(f"Loading ATLAS from: {atlas_path}")
    atlas = load_atlas(atlas_path)

    version = atlas.get("version", "unknown")
    print(f"ATLAS version: {version}")

    # ── Techniques ──────────────────────────────────────────────────────────
    techniques = extract_techniques(atlas)
    print(f"Extracted {len(techniques)} relevant techniques")

    OUTPUT_TECHNIQUES.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_TECHNIQUES.write_text(techniques_to_md(techniques), encoding="utf-8")
    print(f"  → {OUTPUT_TECHNIQUES}")

    # ── Case Studies ─────────────────────────────────────────────────────────
    case_studies = extract_case_studies(atlas)
    print(f"Extracted {len(case_studies)} case studies")

    OUTPUT_CASESTUDIES.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CASESTUDIES.write_text(case_studies_to_md(case_studies), encoding="utf-8")
    print(f"  → {OUTPUT_CASESTUDIES}")

    print("\nDone. Run rag/build_rag_expert1.py next to ingest into ChromaDB.")


if __name__ == "__main__":
    main()
