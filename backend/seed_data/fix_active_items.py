"""
Fill item_pools, unlock_method, and recharge_time for active items.
- pools: from Fandom wiki (same format as passive)
- unlock: from huijiwiki (same format as passive)
- recharge: from huijiwiki infobox

Usage: cd backend && python seed_data/fix_active_items.py
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
    "Boss": "Boss房", "Boss Rush": "Boss Rush", "Planetarium": "天文馆",
    "Library": "图书馆", "Curse Room": "诅咒房", "Golden Chest": "金宝箱",
    "Red Chest": "红宝箱", "Old Chest": "旧宝箱", "Mom's Chest": "妈妈的宝箱",
    "Beggar": "乞丐", "Devil Beggar": "恶魔乞丐", "Bomb Bum": "炸弹乞丐",
    "Shell Game": "赌运气", "Crane Game": "抓娃娃机", "Key Master": "钥匙大师",
    "Baby Shop": "宝宝商店", "Battery Bum": "电池乞丐", "Rotten Beggar": "腐烂乞丐",
    "Wooden Chest": "木宝箱", "Greed Mode Treasure Room": "贪婪宝库房",
    "Greed Mode Shop": "贪婪商店", "Greed Mode Boss": "贪婪Boss房",
    "Greed Mode Curse Room": "贪婪诅咒房", "Greed Mode Secret Room": "贪婪隐藏房",
    "Greed Mode Angel Room": "贪婪天使房", "Greed Mode Devil Room": "贪婪恶魔房",
    "Challenge Room": "挑战房", "Boss Challenge Room": "Boss挑战房",
    "Dice Room": "骰子房", "Bedroom": "卧室", "I Am Error": "错误房",
    "Mega Chest": "大宝箱", "Stone Chest": "石宝箱", "Spiked Chest": "刺宝箱",
    "Eternal Chest": "永恒宝箱", "Haunted Chest": "鬼宝箱", "Locked Chest": "上锁宝箱",
    "Mimic Chest": "宝箱怪",
}


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Fetch pools from Fandom ─────────────────────────────────────────────────

def fetch_pools(item_id: int, name_en: str) -> list[str]:
    """Fetch item pools from Fandom wiki infobox."""
    params = {"action": "parse", "page": name_en, "prop": "text", "format": "json"}
    try:
        r = requests.get(FANDOM, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return []

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return []

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
    return []


def format_pools(pool_names: list[str]) -> list[str]:
    """Convert pool names to [img:pool/xxx] Chinese format."""
    result = []
    for name in pool_names:
        safe = name.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")
        cn = POOL_CN.get(name, name)
        result.append(f"[img:pool/{safe}] {cn}")
    return result


# ─── Fetch unlock + recharge from huijiwiki ──────────────────────────────────

def fetch_huijiwiki_data(item_id: int) -> tuple[str, str]:
    """Fetch unlock_method and recharge_time from huijiwiki C-page.
    Returns (unlock, recharge)."""
    cid = f"C{item_id}"
    params = {"action": "parse", "page": cid, "prop": "text", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return ("", "")

    if "error" in data:
        return ("", "")

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return ("", "")

    soup = BeautifulSoup(html, "html.parser")
    aside = soup.find("aside")
    if aside:
        text = aside.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    # Extract unlock
    unlock = "初始即可获得"
    m = re.search(r"解锁条件\s*(.+?)。", text)
    if m:
        raw = m.group(1).strip()
        if raw and len(raw) > 1:
            unlock = raw

    # Extract recharge
    recharge = ""
    m2 = re.search(r"充能\s+(\d+(?:\.\d+)?(?:\s*秒)?)", text)
    if m2:
        val = m2.group(1).strip()
        if "秒" in val:
            recharge = f"按时间充能（{val}）"
        elif val == "0":
            recharge = "无需充能"
        else:
            recharge = f"{val}格（按房间充能）"

    return (unlock, recharge)


# ─── Cleanup unlock text ────────────────────────────────────────────────────

def cleanup_unlock(text: str, item_name_cn: str) -> str:
    """Clean up huijiwiki unlock text."""
    if not text or text == "初始即可获得":
        return text

    result = text
    # Strip item name prefix
    if item_name_cn and result.startswith(item_name_cn):
        result = result[len(item_name_cn):].strip()
        result = re.sub(r'^[，。、\s]+', '', result)

    # Simplify "通关标记"
    result = re.sub(r'用 (.+?) 获得所有困难模式通关标记', r'使用 \1 在困难模式下获得所有通关标记', result)
    result = re.sub(r'用 (.+?) 获得困难(.+?)通关标记', r'使用 \1 击败困难\2', result)
    result = re.sub(r'用 (.+?) 获得(.+?)通关标记', r'使用 \1 击败 \2', result)
    result = re.sub(r'获得(.+?)通关标记', r'击败 \1', result)
    result = result.replace('获得Boss Rush通关标记', '完成 Boss Rush')
    result = result.replace('击败 所有困难模式', '在困难模式下获得所有通关标记')

    result = re.sub(r'\s+', ' ', result).strip()
    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Filling active items: pools, unlock, recharge")
    print("=" * 50)

    items = load_json("items.json")
    active_items = [(i["id"], i["name_en"], i.get("name_cn", ""))
                    for i in items if i["category"] == "active" and i["id"] <= 732]
    print(f"Active items: {len(active_items)}")

    # Fetch all data in parallel
    results = {}  # item_id -> {pools, unlock, recharge}
    done = 0

    def fetch_all(iid, name_en, name_cn):
        pools = fetch_pools(iid, name_en)
        unlock, recharge = fetch_huijiwiki_data(iid)
        unlock = cleanup_unlock(unlock, name_cn)
        return (iid, {
            "pools": format_pools(pools) if pools else None,
            "unlock": unlock,
            "recharge": recharge,
        })

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_all, iid, name_en, name_cn): iid
                   for iid, name_en, name_cn in active_items}
        for future in as_completed(futures):
            iid, data = future.result()
            results[iid] = data
            done += 1
            if done % 30 == 0:
                has_p = sum(1 for v in results.values() if v["pools"])
                has_u = sum(1 for v in results.values() if v["unlock"] != "初始即可获得")
                has_r = sum(1 for v in results.values() if v["recharge"])
                print(f"  {done}/{len(active_items)} (pools:{has_p} unlock:{has_u} recharge:{has_r})")

    # Apply results
    for item in items:
        if item["id"] in results:
            d = results[item["id"]]
            if d["pools"]:
                item["item_pools"] = d["pools"]
            item["unlock_method"] = d["unlock"]
            if d["recharge"]:
                item["recharge_time"] = d["recharge"]

    save_json("items.json", items)

    # Stats
    ap = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732 and i.get("item_pools"))
    au = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732 and i.get("unlock_method"))
    ar = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732 and i.get("recharge_time"))
    print(f"\nDone: pools={ap}, unlock={au}, recharge={ar} / {len(active_items)}")

    # Samples
    print("\nSamples:")
    for i in items:
        if i["id"] in [33, 35, 105, 145, 164, 284, 347, 356, 584]:
            print(f"  ID {i['id']} {i['name_en']}:")
            print(f"    pools: {i.get('item_pools')}")
            print(f"    unlock: {i.get('unlock_method','')[:100]}")
            print(f"    recharge: {i.get('recharge_time')}")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
