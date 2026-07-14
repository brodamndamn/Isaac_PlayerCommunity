"""
Clean up huijiwiki unlock text to be more readable.
- Strip redundant item name prefix
- Simplify "通关标记" terminology

Usage: cd backend && python seed_data/cleanup_unlock.py
"""
import json
import re
from pathlib import Path

SEED_DIR = Path(__file__).parent


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cleanup_unlock(text: str, item_name_cn: str) -> str:
    """Clean up huijiwiki unlock text."""
    if not text or text == "初始即可获得":
        return text

    result = text

    # Strip item name prefix if present (e.g. "胎儿博士 击败..." -> "击败...")
    if item_name_cn and result.startswith(item_name_cn):
        result = result[len(item_name_cn):].strip()
        # Remove leading space or punctuation
        result = re.sub(r'^[，。、\s]+', '', result)

    # Simplify "通关标记" patterns
    # "用 X 获得所有困难模式通关标记" -> special case
    result = re.sub(r'用 (.+?) 获得所有困难模式通关标记', r'使用 \1 在困难模式下获得所有通关标记', result)
    # "用 X 获得困难Y通关标记" -> "使用 X 击败困难Y"
    result = re.sub(r'用 (.+?) 获得困难(.+?)通关标记', r'使用 \1 击败困难\2', result)
    # "用 X 获得Y通关标记" -> "使用 X 击败 Y"
    result = re.sub(r'用 (.+?) 获得(.+?)通关标记', r'使用 \1 击败 \2', result)
    # "获得Y通关标记" -> "击败 Y"
    result = re.sub(r'获得(.+?)通关标记', r'击败 \1', result)

    # "击败 困难贪婪模式" -> "击败 困难贪婪模式" (already fine)
    # "获得所有困难模式通关标记" -> keep as-is (special case)

    # Special: "Boss Rush通关标记" -> "完成 Boss Rush"
    result = result.replace('获得Boss Rush通关标记', '完成 Boss Rush')

    # Clean up double spaces
    result = re.sub(r'\s+', ' ', result).strip()

    return result


def main():
    items = load_json("items.json")

    updated = 0
    for item in items:
        old = item.get("unlock_method", "")
        if not old or old == "初始即可获得":
            continue

        name_cn = item.get("name_cn", "")
        new = cleanup_unlock(old, name_cn)
        if new != old:
            item["unlock_method"] = new
            updated += 1

    save_json("items.json", items)
    print(f"Cleaned up {updated} unlock texts")

    # Show samples
    samples = [1, 52, 94, 114, 331, 548, 619, 667, 149, 168, 190]
    for item in items:
        if item["id"] in samples:
            print(f"  ID {item['id']} {item['name_en']}: {item.get('unlock_method', '')}")

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    main()
