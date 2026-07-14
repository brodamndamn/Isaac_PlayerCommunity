"""
Re-fetch ALL card effects from huijiwiki K-pages.
Only extract the main "使用后：" section, skip "塔罗牌桌布" synergy.

Usage: cd backend && python seed_data/fix_card_effects.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

HUIJI = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent

# K-page mapping (verified against huijiwiki)
CORRECT_K_MAP = {
    835: 31, 836: 46, 837: 79, 838: 42, 839: 52, 840: 53, 841: 54,
    842: 43, 843: 44, 844: 48, 845: 45, 846: 47, 847: 51, 848: 80,
    849: 32, 850: 33, 851: 34, 852: 35, 853: 36, 854: 37, 855: 38, 856: 39,
    857: 40, 858: 41, 859: 55,
    877: 49, 878: 50, 879: 78,
}


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_k_page(item_id: int) -> str | None:
    """Get K-page ID for a card."""
    if 783 <= item_id <= 804:
        return f"K{item_id - 782}"  # Tarot
    if 805 <= item_id <= 826:
        return f"K{item_id - 749}"  # Reversed
    if 827 <= item_id <= 834:
        return f"K{item_id - 804}"  # Playing cards
    if 860 <= item_id <= 876:
        return f"K{item_id - 779}"  # Soul stones
    if item_id in CORRECT_K_MAP:
        return f"K{CORRECT_K_MAP[item_id]}"
    return None


def extract_effect(extract: str) -> str:
    """Extract only the main effect from huijiwiki extract.
    Gets text between '使用后：' and the next section (塔罗牌桌布 or == heading)."""
    if not extract:
        return ""

    # Find == 效果 == section
    m = re.search(r"==\s*效果\s*==\s*\n+(.*?)(?=\n==\s*[^=]+\s*==|\Z)", extract, re.DOTALL)
    if not m:
        return ""

    section = m.group(1).strip()

    # Extract the main "使用后：" block
    # Start after "使用后：" or "使用后：\n"
    m2 = re.search(r"使用后：\s*\n*(.*?)(?=\n使用后（\s*塔罗牌桌布|$)", section, re.DOTALL)
    if m2:
        effect = m2.group(1).strip()
    else:
        # Some cards might not have "使用后：" format
        # Just take the whole section
        effect = section

    # Clean up LaTeX math (same as before)
    effect = effect.replace('\\(', '').replace('\\)', '')
    effect = effect.replace('\\left\\lfloor', '').replace('\\right\\rfloor', '')
    effect = effect.replace('\\lfloor', '').replace('\\rfloor', '')
    effect = effect.replace('\\left(', '(').replace('\\right)', ')')
    effect = effect.replace('\\left', '').replace('\\right', '')
    effect = effect.replace('\\times', '×')
    effect = effect.replace('\\ge', '≥').replace('\\le', '≤')
    effect = effect.replace('\\max', 'max').replace('\\min', 'min')
    effect = effect.replace('\\%', '%').replace('\\,', '')

    # Subscripts
    effect = re.sub(r'_\{([^}]+)\}', r'\1', effect)

    # Fractions
    for cmd in ['\\dfrac', '\\cfrac', '\\frac']:
        while cmd in effect:
            idx = effect.index(cmd)
            after = effect[idx + len(cmd):]
            if not after.startswith('{'):
                break
            depth = 0
            b1 = -1
            for i, ch in enumerate(after):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: b1 = i; break
            if b1 <= 0: break
            x = after[1:b1]
            rest = after[b1 + 1:]
            if not rest.startswith('{'): break
            depth = 0
            b2 = -1
            for i, ch in enumerate(rest):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: b2 = i; break
            if b2 <= 0: break
            y = rest[1:b2]
            effect = effect[:idx] + f'{x}/{y}' + rest[b2 + 1:]

    # Clean up whitespace
    effect = re.sub(r'\n{3,}', '\n\n', effect)
    effect = re.sub(r' +', ' ', effect)
    effect = effect.strip()

    return effect


def fetch_card_effect(item_id: int) -> tuple[int, str]:
    """Fetch Chinese effect for a single card."""
    k_page = get_k_page(item_id)
    if not k_page:
        return (item_id, "")

    params = {"action": "query", "titles": k_page, "prop": "extracts", "explaintext": 1, "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return (item_id, "")

    if "error" in data:
        return (item_id, "")

    for page in data.get("query", {}).get("pages", {}).values():
        extract = page.get("extract", "")
        effect = extract_effect(extract)
        return (item_id, effect)

    return (item_id, "")


def main():
    print("Re-fetching ALL card effects from huijiwiki...")
    print("=" * 50)

    items = load_json("items.json")
    cards = [i for i in items if i["category"] == "card"]
    print(f"Cards: {len(cards)}")

    results = {}
    done = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_card_effect, c["id"]): c["id"] for c in cards}
        for future in as_completed(futures):
            iid, effect = future.result()
            results[iid] = effect
            done += 1
            if done % 20 == 0:
                has = sum(1 for v in results.values() if v)
                print(f"  {done}/{len(cards)} (got effect: {has})")

    # Apply results
    updated = 0
    skipped = 0
    for item in items:
        if item["id"] in results:
            effect = results[item["id"]]
            if effect:
                item["effect"] = effect
                updated += 1
            else:
                skipped += 1

    save_json("items.json", items)

    print(f"\nDone: updated {updated}, skipped (no effect found) {skipped}")

    # Show samples
    with open(SEED_DIR / "_card_after.txt", "w", encoding="utf-8") as f:
        for item in items:
            if item["category"] == "card" and item["id"] in [783, 784, 785, 792, 793, 794]:
                f.write(f'ID {item["id"]} {item["name_en"]}:\n')
                f.write(f'  effect: {item.get("effect","")[:300]}\n\n')

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
