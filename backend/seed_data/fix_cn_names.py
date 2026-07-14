"""
Re-fetch ALL card/rune/special Chinese names with CORRECT K-page mappings.
The old mappings were completely swapped between runes and special cards.

Correct K-page mapping (verified against huijiwiki):
- K1-K22: Tarot cards (ID-782)
- K23-K30: Playing cards (ID-804)
- K31: Joker
- K32-K41: Runes (Hagalaz through Black Rune)
- K42-K55: Special cards
- K55: Rune Shard
- K56-K77: Reversed tarot (ID-749)
- K78: Cracked Key
- K79: Queen of Hearts
- K80: Wild Card
- K81-K97: Soul stones (ID-779)

Usage: cd backend && python seed_data/fix_cn_names.py
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

# ─── CORRECT K-page mappings ────────────────────────────────────────────────

# For special cards (IDs 835-848) and misc (877-879)
CORRECT_K_MAP = {
    # Special cards
    835: 31,   # Joker → K31 鬼牌
    836: 46,   # Suicide King → K46 自杀之王
    837: 79,   # Queen of Hearts → K79 红桃Q
    838: 42,   # Chaos Card → K42 混沌卡
    839: 52,   # Huge Growth → K52 变巨术
    840: 53,   # Ancient Recall → K53 先祖召唤
    841: 54,   # Era Walk → K54 时空漫步
    842: 43,   # Credit Card → K43 信用卡
    843: 44,   # Rules Card → K44 规则卡
    844: 48,   # ? Card → K48 ？卡
    845: 45,   # A Card Against Humanity → K45 反人类卡
    846: 47,   # Get out of Jail Free Card → K47 免费保释卡
    847: 51,   # Holy Card → K51 神圣卡
    848: 80,   # Wild Card → K80 万用牌
    # Runes (formula: K = 32 + index within rune list)
    849: 32,   # Rune of Hagalaz → K32 冰雹符文
    850: 33,   # Rune of Jera → K33 收获符文
    851: 34,   # Rune of Ehwaz → K34 马骑符文
    852: 35,   # Rune of Dagaz → K35 朝夕符文
    853: 36,   # Rune of Ansuz → K36 诸神符文
    854: 37,   # Rune of Perthro → K37 签筒符文
    855: 38,   # Rune of Berkano → K38 桦木符文
    856: 39,   # Rune of Algiz → K39 保护符文
    857: 40,   # Blank Rune → K40 空白符文
    858: 41,   # Black Rune → K41 黑符文
    859: 55,   # Rune Shard → K55 符文碎片
    # Misc
    877: 49,   # Dice Shard → K49 骰子碎片
    878: 50,   # Emergency Contact → K50 紧急联系电话
    879: 78,   # Cracked Key → K78 红钥匙碎片
}


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Get huijiwiki page ID ─────────────────────────────────────────────────

def get_k_page_id(item_id: int) -> str | None:
    """Get K-page number for a card item (IDs 783-879)."""
    # Tarot 783-804
    if 783 <= item_id <= 804:
        return f"K{item_id - 782}"
    # Reversed tarot 805-826
    if 805 <= item_id <= 826:
        return f"K{item_id - 749}"
    # Playing cards 827-834
    if 827 <= item_id <= 834:
        return f"K{item_id - 804}"
    # Soul stones 860-876
    if 860 <= item_id <= 876:
        return f"K{item_id - 779}"
    # Special / Runes / Misc — hardcoded
    if item_id in CORRECT_K_MAP:
        return f"K{CORRECT_K_MAP[item_id]}"
    return None


# ─── Fetch Chinese name ────────────────────────────────────────────────────

def fetch_cn_name(page_id: str) -> str:
    """Fetch Chinese displaytitle, including full-width ？！."""
    if not page_id:
        return ""

    params = {"action": "parse", "page": page_id, "prop": "displaytitle", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=15)
        data = r.json()
    except Exception:
        return ""

    if "error" in data:
        return ""

    title_html = data.get("parse", {}).get("displaytitle", "")
    if not title_html:
        return ""

    clean = re.sub(r"<[^>]+>", " ", title_html).strip()
    clean = re.sub(r"^[IVX0-9]+-\s*", "", clean).strip()

    # Extract Chinese characters + full-width punctuation
    m = re.search(r"[一-鿿㐀-䶿?!？！]+", clean)
    if m:
        return m.group(0)

    return ""


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Re-fetch ALL card Chinese names with correct K-page mapping")
    print("=" * 60)

    items = load_json("items.json")

    # Collect all items to re-fetch:
    # 1. Cards with hardcoded K mappings (likely wrong) → IDs 835-848, 849-859, 877-879
    # 2. ALL cards without CN names (from earlier scan)
    # 3. Reversed tarot (to ensure ？ is present)

    cards_to_fix = set()
    for i in items:
        if i["category"] != "card":
            continue
        iid = i["id"]

        # All cards that use hardcoded mapping need re-fetch
        if iid in CORRECT_K_MAP:
            cards_to_fix.add(iid)
        # Cards without CN name
        if not i.get("name_cn"):
            cards_to_fix.add(iid)
        # Reversed tarot - always re-fetch for ？
        if 805 <= iid <= 826:
            cards_to_fix.add(iid)

    # Also collect non-card items without CN
    other_to_fix = set()
    for i in items:
        if i["category"] != "card" and not i.get("name_cn"):
            other_to_fix.add(i["id"])

    print(f"Cards to re-fetch: {len(cards_to_fix)}")
    print(f"Non-cards to fix: {len(other_to_fix)}")

    # Re-fetch all cards
    updated = 0
    for item in items:
        if item["id"] in cards_to_fix:
            page_id = get_k_page_id(item["id"])
            if page_id:
                name_cn = fetch_cn_name(page_id)
                if name_cn:
                    old = item.get("name_cn", "")
                    item["name_cn"] = name_cn
                    if old != name_cn:
                        updated += 1

    print(f"Card names updated: {updated}")

    # Handle non-card items (pills, trinkets, collectibles)
    # Pills: P-pages
    # Collectibles: C-pages
    for item in items:
        if item["id"] not in other_to_fix:
            continue
        if item["category"] == "pill":
            page_id = f"P{item['id'] - 733}"
        elif item["id"] <= 732:
            page_id = f"C{item['id']}"
        else:
            continue

        name_cn = fetch_cn_name(page_id)
        if name_cn:
            item["name_cn"] = name_cn
        elif item["id"] == 15:  # <3
            item["name_cn"] = "<3"

    # Save
    save_json("items.json", items)

    # Report
    no_cn = [(i["id"], i["name_en"], i["category"]) for i in items if not i.get("name_cn")]
    print(f"\nItems still without CN: {len(no_cn)}")
    for iid, name, cat in no_cn:
        print(f"  ID {iid}: {name} ({cat})")

    # Spot-check key items
    print("\nSpot-check (correct mapping verification):")
    checks = [
        (835, "Joker", "鬼牌"),
        (849, "Rune of Hagalaz", "冰雹符文"),
        (842, "Credit Card", "信用卡"),
        (847, "Holy Card", "神圣卡"),
        (805, "0 - The Fool?", "愚者？"),
        (807, "II - The High Priestess?", "女祭司？"),
    ]
    for iid, name_en, expected_cn in checks:
        item = next((i for i in items if i["id"] == iid), None)
        if item:
            cn = item.get("name_cn", "")
            ok = "✅" if expected_cn in cn else "❌"
            print(f"  {ok} ID {iid} ({name_en}): CN=\"{cn}\" (expected: \"{expected_cn}\")")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    main()
