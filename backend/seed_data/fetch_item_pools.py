"""
Fetch item pools for passive items from Fandom wiki.
Format: ["[pool:english_name] Chinese Name", ...]

Usage: cd backend && python seed_data/fetch_item_pools.py
"""
import asyncio
import json
import re
import time
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent

# Pool name → Chinese translation
POOL_CN = {
    "Treasure Room": "宝库房",
    "Devil Room": "恶魔房",
    "Angel Room": "天使房",
    "Secret Room": "隐藏房",
    "Ultra Secret Room": "超隐藏房",
    "Shop": "商店",
    "Boss": "Boss房",
    "Boss Rush": "Boss Rush",
    "Planetarium": "天文馆",
    "Library": "图书馆",
    "Curse Room": "诅咒房",
    "Golden Chest": "金宝箱",
    "Red Chest": "红宝箱",
    "Old Chest": "旧宝箱",
    "Mom's Chest": "妈妈的宝箱",
    "Beggar": "乞丐",
    "Devil Beggar": "恶魔乞丐",
    "Bomb Bum": "炸弹乞丐",
    "Shell Game": "赌运气",
    "Crane Game": "抓娃娃机",
    "Key Master": "钥匙大师",
    "Greed Mode Treasure Room": "贪婪宝库房",
    "Greed Mode Shop": "贪婪商店",
    "Greed Mode Boss": "贪婪Boss房",
    "Greed Mode Curse Room": "贪婪诅咒房",
    "Greed Mode Secret Room": "贪婪隐藏房",
    "Greed Mode Angel Room": "贪婪天使房",
    "Greed Mode Devil Room": "贪婪恶魔房",
    "Challenge Room": "挑战房",
    "Boss Challenge Room": "Boss挑战房",
    "Dice Room": "骰子房",
    "Bedroom": "卧室",
    "I Am Error": "错误房",
    "Mega Chest": "大宝箱",
    "Stone Chest": "石宝箱",
    "Spiked Chest": "刺宝箱",
    "Eternal Chest": "永恒宝箱",
    "Haunted Chest": "鬼宝箱",
    "Locked Chest": "上锁宝箱",
    "Mimic Chest": "宝箱怪",
    "Baby Shop": "宝宝商店",
    "Battery Bum": "电池乞丐",
    "Rotten Beggar": "腐烂乞丐",
    "Wooden Chest": "木宝箱",
}


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_pools(html: str) -> list[str]:
    """Extract item pools from Fandom wiki infobox HTML."""
    soup = BeautifulSoup(html, "html.parser")

    for attr in soup.find_all(attrs={"data-source": True}):
        if attr.get("data-source") != "alias":
            continue
        value_div = attr.find(class_="pi-data-value")
        if not value_div:
            continue

        links = value_div.find_all("a")
        pool_names = []
        for a in links:
            text = a.get_text(strip=True)
            # Skip grid position links (contain digits and slashes)
            if text and not re.search(r"[\(\d]", text) and "/" not in text:
                pool_names.append(text)

        if pool_names:
            # Deduplicate while preserving order
            seen = set()
            unique = []
            for p in pool_names:
                if p not in seen:
                    seen.add(p)
                    unique.append(p)
            return unique

    return []


def format_pools(pool_names: list[str]) -> list[str]:
    """Convert pool names to [pool:xxx] Chinese format."""
    result = []
    for name in pool_names:
        # Create a safe key from the English name
        safe_key = name.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")
        cn_name = POOL_CN.get(name, name)  # Fallback to English if no translation
        placeholder = f"[pool:{safe_key}]"
        result.append(f"{placeholder} {cn_name}")
    return result


async def fetch_item_pools(session: aiohttp.ClientSession, item_id: int, name_en: str, sem: asyncio.Semaphore) -> tuple[int, list[str]]:
    """Fetch item pools for a single item. Returns (item_id, formatted_pools)."""
    async with sem:
        params = {"action": "parse", "page": name_en, "prop": "text", "format": "json"}
        try:
            async with session.get(WIKI_API, params=params) as resp:
                data = await resp.json()
        except Exception:
            return (item_id, [])

        html = data.get("parse", {}).get("text", {}).get("*", "")
        if not html:
            return (item_id, [])

        pools = parse_pools(html)
        formatted = format_pools(pools)
        return (item_id, formatted)


async def main():
    print("Fetching item pools for passive items...")
    print("=" * 50)

    items = load_json("items.json")
    passive = [(i["id"], i["name_en"]) for i in items if i["category"] == "passive" and i["id"] <= 732]
    print(f"Passive items to process: {len(passive)}")

    sem = asyncio.Semaphore(15)
    connector = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks = [fetch_item_pools(session, iid, name, sem) for iid, name in passive]

        done = 0
        pools_map: dict[int, list[str]] = {}
        for coro in asyncio.as_completed(tasks):
            iid, pools = await coro
            if pools:
                pools_map[iid] = pools
            done += 1
            if done % 50 == 0:
                print(f"  Progress: {done}/{len(passive)} (found pools for {len(pools_map)})")

    # Update items.json
    updated = 0
    for item in items:
        if item["id"] in pools_map:
            item["item_pools"] = pools_map[item["id"]]
            updated += 1

    save_json("items.json", items)

    # Stats
    no_pools = sum(1 for i in items if i["category"] == "passive" and i["id"] <= 732 and not i.get("item_pools"))
    print(f"\nDone: updated {updated}, still without pools: {no_pools}")

    # Show some samples
    print("\nSample results:")
    samples = [1, 118, 182, 330, 415, 548, 619]
    for i in items:
        if i["id"] in samples:
            print(f"  ID {i['id']} {i['name_en']}: {i.get('item_pools', [])}")

    # Track unknown pool names
    all_pools = set()
    for pools_list in pools_map.values():
        for p in pools_list:
            # Extract pool key
            m = re.search(r"\[pool:(.+?)\]", p)
            if m:
                all_pools.add(m.group(1))

    known = set(POOL_CN.keys())
    unknown_eng = set()
    for p in all_pools:
        eng = p.replace("_", " ").title()
        if eng not in known:
            # Try to find in POOL_CN keys
            found = False
            for k in known:
                if k.lower().replace(" ", "_").replace("'", "") == p:
                    found = True
                    break
            if not found:
                unknown_eng.add(p)

    if unknown_eng:
        print(f"\nUnknown pools (need translation): {len(unknown_eng)}")
        for p in sorted(unknown_eng):
            print(f"  {p}")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\nTotal time: {time.time() - start:.1f}s")
