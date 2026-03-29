"""
fix_expert3_violations.py

修复 training_data_expert3_final_fixed.jsonl 中 un_principle_violations 字段：
  - risk_tier == "MINIMAL" 且 recommendation == "APPROVE"  → violations 清空为 []
  - risk_tier == "LIMITED" 且 recommendation == "APPROVE"  → 保留原值
  - 其他组合                                               → 不动

输出到 expert3_training_data_v2.jsonl
"""

import json
import re
from collections import defaultdict
from pathlib import Path

INPUT_FILE  = "training_data_expert3_final_fixed.jsonl"
OUTPUT_FILE = "expert3_training_data_v2.jsonl"


def parse_assistant_json(content: str) -> dict:
    """
    解析 assistant 内容中的 JSON。
    兼容两种格式：
      1. 纯 JSON（无 markdown 包装）
      2. ```json ... ``` 包装
    """
    # 尝试直接解析
    stripped = content.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 尝试剥离 markdown 代码块
    match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', stripped)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"无法解析 assistant JSON:\n{content[:300]}")


def main():
    samples = []
    with open(INPUT_FILE, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  第 {lineno} 行 JSON 解析失败: {e}")

    print(f"读取 {len(samples)} 个样本\n")

    fixed_count   = 0
    kept_count    = 0
    skipped_count = 0
    error_count   = 0

    # 统计每种 tier+rec 组合
    combo_stats   = defaultdict(lambda: {"total": 0, "fixed": 0, "kept": 0})

    output_samples = []

    for i, sample in enumerate(samples):
        messages = sample.get("messages", [])
        assistant_idx = next(
            (j for j, m in enumerate(messages) if m["role"] == "assistant"), None
        )

        if assistant_idx is None:
            print(f"  样本 {i}: 没有 assistant 消息，跳过")
            skipped_count += 1
            output_samples.append(sample)
            continue

        raw_content = messages[assistant_idx]["content"]

        try:
            data = parse_assistant_json(raw_content)
        except ValueError as e:
            print(f"  样本 {i}: {e}")
            error_count += 1
            output_samples.append(sample)
            continue

        tier = data.get("risk_tier", "")
        rec  = data.get("recommendation", "")
        combo_key = f"{tier}+{rec}"
        combo_stats[combo_key]["total"] += 1

        original_violations = data.get("un_principle_violations", [])

        if tier == "MINIMAL" and rec == "APPROVE":
            # 修复：清空 violations
            if original_violations:  # 只有非空才算修复
                data["un_principle_violations"] = []
                fixed_count += 1
                combo_stats[combo_key]["fixed"] += 1
            else:
                kept_count += 1
                combo_stats[combo_key]["kept"] += 1
        else:
            # 所有其他组合：不动
            kept_count += 1
            combo_stats[combo_key]["kept"] += 1

        # 重新序列化为纯 JSON（不加 markdown 包装）
        new_content = json.dumps(data, ensure_ascii=False)
        new_messages = list(messages)
        new_messages[assistant_idx] = {
            "role": "assistant",
            "content": new_content,
        }
        output_samples.append({"messages": new_messages})

    # 写输出
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for s in output_samples:
            out.write(json.dumps(s, ensure_ascii=False) + "\n")

    # 统计报告
    print("=" * 55)
    print(f"修复完成 → {OUTPUT_FILE}")
    print("=" * 55)
    print(f"  总样本数  : {len(samples)}")
    print(f"  实际修复  : {fixed_count}  （MINIMAL+APPROVE violations 清空）")
    print(f"  保留不动  : {kept_count}")
    print(f"  解析错误  : {error_count}")
    print(f"  无assistant: {skipped_count}")

    print("\n各 risk_tier + recommendation 组合统计：")
    print(f"  {'组合':<30} {'总数':>6} {'修复':>6} {'保留':>6}")
    print("  " + "-" * 48)
    for combo, stat in sorted(combo_stats.items()):
        marker = " ← 已修复" if stat["fixed"] > 0 else ""
        print(f"  {combo:<30} {stat['total']:>6} {stat['fixed']:>6} {stat['kept']:>6}{marker}")


if __name__ == "__main__":
    main()
