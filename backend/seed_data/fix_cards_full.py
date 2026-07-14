"""
Fill item_pools, unlock_method, stat_changes for all cards.
Same format and method as passive/active items.

Usage: cd backend && python seed_data/fix_cards_full.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup

FANDOM = "https://bindingofisaacrebirth.fandom.com/api.php"
HUIJI = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent

POOL_CN = {
    "Treasure Room": "宝库房", "Devil Room": "恶魔房", "Angel Room": "天使房",
    "Secret Room": "隐藏房", "Ultra Secret Room": "超隐藏房", "Shop": "商店",
    "Boss": "Boss房", "Library": "图书馆", "Golden Chest": "金宝箱",
    "Red Chest": "红宝箱", "Curse Room": "诅咒房",
    "Beggar": "乞丐", "Devil Beggar": "恶魔乞丐", "Bomb Bum": "炸弹乞丐",
    "Shell Game": "赌运气", "Crane Game": "抓娃娃机", "Key Master": "钥匙大师",
    "Challenge Room": "挑战房", "Boss Challenge Room": "Boss挑战房",
    "Bedroom": "卧室", "Dice Room": "骰子房", "Planetarium": "天文馆",
    "Wooden Chest": "木宝箱", "Mega Chest": "大宝箱", "Mom's Chest": "妈妈的宝箱",
    "Old Chest": "旧宝箱",
}

# K-page mapping for cards
CORRECT_K_MAP = {
    835: 31, 836: 46, 837: 79, 838: 42, 839: 52, 840: 53, 841: 54,
    842: 43, 843: 44, 844: 48, 845: 45, 846: 47, 847: 51, 848: 80,
    849: 32, 850: 33, 851: 34, 852: 35, 853: 36, 854: 37, 855: 38, 856: 39,
    857: 40, 858: 41, 859: 55,
    877: 49, 878: 50, 879: 78,
}

# Stat extraction patterns
STAT_TYPES = [
    ('damage', '伤害', [r'伤害\s*([+\-]?\d+\.?\d*)', r'伤害修正\s*[×xX]\s*(\d+\.?\d*)\s*%']),
    ('tears', '射速', [r'射速\s*([+\-]?\d+\.?\d*)', r'射速修正\s*[×xX]\s*(\d+\.?\d*)\s*%']),
    ('speed', '移速', [r'移速\s*([+\-]?\d+\.?\d*)']),
    ('range', '射程', [r'射程\s*([+\-]?\d+\.?\d*)']),
    ('shot_speed', '弹速', [r'弹速\s*([+\-]?\d+\.?\d*)']),
    ('luck', '幸运', [r'幸运\s*([+\-]?\d+\.?\d*)']),
    ('health', '生命', [r'获得\s*(\d+)\s*个心之容器']),
    ('soul_heart', '魂心', [r'(\d+)\s*个魂心']),
    ('black_heart', '黑心', [r'(\d+)\s*个黑心']),
    ('eternal_heart', '永恒之心', [r'(\d+)\s*个永恒之心']),
    ('bomb', '炸弹', [r'(\d+)\s*个炸弹']),
    ('coin', '硬币', [r'(\d+)\s*个硬币']),
    ('key', '钥匙', [r'(\d+)\s*个钥匙']),
]


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── K-page helper ───────────────────────────────────────────────────────────

def get_k_page(item_id: int) -> str | None:
    if 783 <= item_id <= 804:
        return f"K{item_id - 782}"
    if 805 <= item_id <= 826:
        return f"K{item_id - 749}"
    if 827 <= item_id <= 834:
        return f"K{item_id - 804}"
    if 860 <= item_id <= 876:
        return f"K{item_id - 779}"
    if item_id in CORRECT_K_MAP:
        return f"K{CORRECT_K_MAP[item_id]}"
    return None


# ─── Pools from Fandom ──────────────────────────────────────────────────────

def fetch_pools(name_en: str) -> list[str] | None:
    params = {"action": "parse", "page": name_en, "prop": "text", "format": "json"}
    try:
        r = requests.get(FANDOM, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return None
    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for attr in soup.find_all(attrs={"data-source": True}):
        if attr.get("data-source") != "alias":
            continue
        value_div = attr.find(class_="pi-data-value")
        if not value_div:
            continue
        links = value_div.find_all("a")
        pools = []
        for a in links:
            text = a.get_text(strip=True)
            if text and not re.search(r"[\(\d]", text) and "/" not in text:
                pools.append(text)
        if pools:
            seen = set()
            unique = []
            for p in pools:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique
    return None


def format_pools(names: list[str]) -> list[str]:
    result = []
    for name in names:
        safe = name.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")
        cn = POOL_CN.get(name, name)
        result.append(f"[img:pool/{safe}] {cn}")
    return result


# ─── Unlock from huijiwiki ──────────────────────────────────────────────────

def fetch_unlock(item_id: int) -> str:
    k_page = get_k_page(item_id)
    if not k_page:
        return "初始即可获得"

    params = {"action": "parse", "page": k_page, "prop": "text", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return "初始即可获得"
    if "error" in data:
        return "初始即可获得"

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return "初始即可获得"

    soup = BeautifulSoup(html, "html.parser")
    aside = soup.find("aside")
    text = (aside or soup).get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    m = re.search(r"解锁条件\s*(.+?)。", text)
    if m:
        raw = m.group(1).strip()
        if raw and len(raw) > 1:
            return raw
    return "初始即可获得"


def cleanup_unlock(text: str, name_cn: str) -> str:
    if not text or text == "初始即可获得":
        return text
    result = text
    if name_cn and result.startswith(name_cn):
        result = result[len(name_cn):].strip()
        result = re.sub(r'^[，。、\s]+', '', result)
    result = re.sub(r'用 (.+?) 获得所有困难模式通关标记', r'使用 \1 在困难模式下获得所有通关标记', result)
    result = re.sub(r'用 (.+?) 获得困难(.+?)通关标记', r'使用 \1 击败困难\2', result)
    result = re.sub(r'用 (.+?) 获得(.+?)通关标记', r'使用 \1 击败 \2', result)
    result = re.sub(r'获得(.+?)通关标记', r'击败 \1', result)
    result = result.replace('获得Boss Rush通关标记', '完成 Boss Rush')
    result = re.sub(r'\s+', ' ', result).strip()
    return result


# ─── Stat changes ────────────────────────────────────────────────────────────

def extract_stats(effect: str) -> list[list[str]]:
    results = []
    for key, cn_name, patterns in STAT_TYPES:
        for pat in patterns:
            m = re.search(pat, effect)
            if not m:
                continue
            value = m.group(1)
            if re.match(r'^\d+\.?\d*$', value):
                value = '+' + value
            attr = f'[img:stat/{key}] {cn_name}'
            if not any(r[0] == attr for r in results):
                results.append([attr, value])
            break
    return results


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Filling cards: pools + unlock + stat_changes")
    print("=" * 50)

    items = load_json("items.json")
    cards = [(i["id"], i["name_en"], i.get("name_cn", "")) for i in items if i["category"] == "card"]
    print(f"Cards: {len(cards)}")

    results = {}
    done = 0

    def fetch_one(iid, name_en, name_cn):
        pools = fetch_pools(name_en)
        unlock = cleanup_unlock(fetch_unlock(iid), name_cn)
        return (iid, {
            "pools": format_pools(pools) if pools else None,
            "unlock": unlock,
        })

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_one, iid, name_en, name_cn): iid
                   for iid, name_en, name_cn in cards}
        for future in as_completed(futures):
            iid, data = future.result()
            results[iid] = data
            done += 1
            if done % 25 == 0:
                has_p = sum(1 for v in results.values() if v["pools"])
                has_u = sum(1 for v in results.values() if v["unlock"] != "初始即可获得")
                print(f"  {done}/{len(cards)} (pools:{has_p} unlock:{has_u})")

    # Apply and extract stats
    pools_count = 0
    unlock_count = 0
    stat_count = 0

    for item in items:
        if item["id"] not in results:
            continue
        d = results[item["id"]]
        if d["pools"]:
            item["item_pools"] = d["pools"]
            pools_count += 1
        item["unlock_method"] = d["unlock"]
        if d["unlock"] != "初始即可获得":
            unlock_count += 1

        # Stat changes
        effect = item.get("effect", "")
        if effect:
            stats = extract_stats(effect)
            if stats:
                item["stat_changes"] = stats
                stat_count += 1
            elif "stat_changes" in item:
                del item["stat_changes"]

    # Cards without specific pools get a default
    for item in items:
        if item["category"] == "card" and not item.get("item_pools"):
            item["item_pools"] = ["[img:pool/card_drop] 卡牌掉落"]

    save_json("items.json", items)

    print(f"\nDone: pools={pools_count}, unlock={unlock_count}, stat_changes={stat_count} / {len(cards)}")

    # Samples
    with open(SEED_DIR / "_cards_done.txt", "w", encoding="utf-8") as f:
        for item in items:
            if item["id"] in [783, 784, 792, 796, 835, 849]:
                f.write(f'ID {item["id"]} {item["name_en"]}:\n')
                f.write(f'  pools: {item.get("item_pools")}\n')
                f.write(f'  unlock: {item.get("unlock_method","")}\n')
                f.write(f'  stat_changes: {item.get("stat_changes")}\n\n')

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
