"""
Extract stat changes from Chinese effect text for passive items.
Output format: stat_changes array of [attribute, change] pairs.
Attribute format: "[img:stat/xxx] ChineseName"

Usage: cd backend && python seed_data/extract_stats.py
"""
import json
import re
from pathlib import Path

SEED_DIR = Path(__file__).parent

# Stat types and their image keys + Chinese names
STAT_TYPES = [
    # (key, chinese_name, patterns)
    ("damage", "伤害", [
        r"伤害\s*([+\-]?\d+\.?\d*)",
        r"伤害\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"伤害\s*(减少|降低|下降)\s*(\d+\.?\d*)",
        r"伤害修正\s*[×xX]\s*(\d+\.?\d*)\s*%",
        r"伤害\s*[×xX]\s*(\d+\.?\d*)\s*%",
        r"伤害修正\s*[×xX]\s*(\d+\.?\d*/\d+\.?\d*)",
    ]),
    ("tears", "射速", [
        r"射速\s*([+\-]?\d+\.?\d*)",
        r"射速\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"射速\s*(减少|降低|下降)\s*(\d+\.?\d*)",
        r"射速修正\s*[×xX]\s*(\d+\.?\d*)\s*%",
        r"射速\s*[×xX]\s*(\d+\.?\d*)\s*%",
        r"射速修正\s*[×xX]\s*(\d+\.?\d*/\d+\.?\d*)",
    ]),
    ("speed", "移速", [
        r"移速\s*([+\-]?\d+\.?\d*)",
        r"移速\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"移速\s*(减少|降低|下降)\s*(\d+\.?\d*)",
    ]),
    ("range", "射程", [
        r"射程\s*([+\-]?\d+\.?\d*)",
        r"射程\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"射程修正\s*[×xX]\s*(\d+\.?\d*)\s*%",
    ]),
    ("shot_speed", "弹速", [
        r"弹速\s*([+\-]?\d+\.?\d*)",
        r"弹速\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"弹速\s*(减少|降低|下降)\s*(\d+\.?\d*)",
    ]),
    ("luck", "幸运", [
        r"幸运\s*([+\-]?\d+\.?\d*)",
        r"幸运\s*(增加|提升|上升|提高)\s*(\d+\.?\d*)",
        r"幸运\s*(减少|降低|下降)\s*(\d+\.?\d*)",
    ]),
    ("health", "生命", [
        r"获得\s*(\d+)\s*个心之容器",
        r"给予\s*(\d+)\s*个心之容器",
        r"增加\s*(\d+)\s*个心之容器",
    ]),
    ("soul_heart", "魂心", [
        r"获得\s*(\d+)\s*个魂心",
        r"给予\s*(\d+)\s*个魂心",
        r"(\d+)\s*个魂心",
    ]),
    ("black_heart", "黑心", [
        r"获得\s*(\d+)\s*个黑心",
        r"给予\s*(\d+)\s*个黑心",
        r"(\d+)\s*个黑心",
    ]),
    ("eternal_heart", "永恒之心", [
        r"获得\s*(\d+)\s*个永恒之心",
    ]),
    ("bomb", "炸弹", [
        r"获得\s*(\d+)\s*个炸弹",
        r"(\d+)\s*炸弹",
    ]),
    ("coin", "硬币", [
        r"获得\s*(\d+)\s*个硬币",
        r"(\d+)\s*个硬币",
    ]),
    ("key", "钥匙", [
        r"获得\s*(\d+)\s*个钥匙",
        r"(\d+)\s*钥匙",
    ]),
]


def extract_stats(effect: str) -> list[list[str]]:
    """Extract stat changes from Chinese effect text.
    Returns list of [attribute_placeholder, change_value] pairs."""
    results = []

    for key, cn_name, patterns in STAT_TYPES:
        for pat in patterns:
            m = re.search(pat, effect)
            if not m:
                continue

            value = ""
            groups = m.groups()

            if len(groups) == 1:
                raw = groups[0]
                # Check if it looks like a number
                if re.match(r'^[+\-]?\d+\.?\d*$', raw):
                    value = raw
                    if not value.startswith("+") and not value.startswith("-"):
                        value = "+" + value
                elif re.match(r'^\d+$', raw):
                    value = "+" + raw
                else:
                    value = raw
            elif len(groups) == 2:
                keyword = groups[0]
                num = groups[1]
                if keyword in ("增加", "提升", "上升", "提高"):
                    value = "+" + num
                elif keyword in ("减少", "降低", "下降"):
                    value = "-" + num
                else:
                    value = groups[0]  # raw match

            if value and value != "":
                attr = f"[img:stat/{key}] {cn_name}"
                # Avoid duplicates for the same stat
                if not any(r[0] == attr for r in results):
                    results.append([attr, value])
                break  # first match for this stat type

    return results


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    items = load_json("items.json")
    passive = [i for i in items if i["category"] == "passive" and i["id"] <= 732]

    updated = 0
    for item in passive:
        effect = item.get("effect", "")
        if not effect:
            continue

        stats = extract_stats(effect)
        if stats:
            item["stat_changes"] = stats
            updated += 1
        elif "stat_changes" in item:
            del item["stat_changes"]  # Remove if no longer applicable

    save_json("items.json", items)
    print(f"Items with stat changes: {updated} / {len(passive)}")

    # Show samples
    samples = [1, 4, 6, 12, 79, 101, 118, 182, 330]
    print("\nSamples:")
    for item in items:
        if item["id"] in samples:
            stats = item.get("stat_changes", [])
            print(f"ID {item['id']} {item['name_en']}: {stats}")

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    main()
