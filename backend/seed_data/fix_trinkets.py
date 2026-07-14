"""
Fill unlock_method and stat_changes for trinkets.
Trinkets don't have traditional item pools, so pools are skipped.

Usage: cd backend && python seed_data/fix_trinkets.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HUIJI = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Fetch unlock from huijiwiki T-page ──────────────────────────────────────

def fetch_trinket_data(our_id: int, game_tid: int) -> tuple[str, str | None]:
    """Fetch unlock_method from huijiwiki T-page.
    game_tid: the in-game trinket ID (1-191)."""
    cid = f"T{game_tid}"
    params = {"action": "parse", "page": cid, "prop": "text", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return ("初始即可获得", None)

    if "error" in data:
        return ("初始即可获得", None)

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return ("初始即可获得", None)

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

    return (unlock, None)


def cleanup_unlock(text: str, item_name_cn: str) -> str:
    """Clean up huijiwiki unlock text."""
    if not text or text == "初始即可获得":
        return text
    result = text
    if item_name_cn and result.startswith(item_name_cn):
        result = result[len(item_name_cn):].strip()
        result = re.sub(r'^[，。、\s]+', '', result)
    result = re.sub(r'用 (.+?) 获得所有困难模式通关标记', r'使用 \1 在困难模式下获得所有通关标记', result)
    result = re.sub(r'用 (.+?) 获得困难(.+?)通关标记', r'使用 \1 击败困难\2', result)
    result = re.sub(r'用 (.+?) 获得(.+?)通关标记', r'使用 \1 击败 \2', result)
    result = re.sub(r'获得(.+?)通关标记', r'击败 \1', result)
    result = result.replace('获得Boss Rush通关标记', '完成 Boss Rush')
    result = result.replace('击败 所有困难模式', '在困难模式下获得所有通关标记')
    result = re.sub(r'\s+', ' ', result).strip()
    return result


# ─── Stat extraction ─────────────────────────────────────────────────────────

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
]

def extract_stats(effect):
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


# ─── Build game trinket ID mapping from wiki.gg ──────────────────────────────

def get_trinket_game_id_map(items):
    """Map our item IDs -> game trinket IDs using wiki.gg Trinkets table."""
    WIKI_GG = "https://bindingofisaacrebirth.wiki.gg/api.php"
    params = {"action": "parse", "page": "Trinkets", "prop": "text", "format": "json"}
    try:
        r = requests.get(WIKI_GG, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return {}

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        return {}

    name_to_gid = {}
    for row in tables[0].find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        name_link = cells[0].find("a")
        if not name_link:
            continue
        name = name_link.get("title", "").strip()
        id_text = cells[1].get_text(strip=True)
        m = re.search(r"5\.350\.(\d+)", id_text)
        if m:
            name_to_gid[name] = int(m.group(1))

    result = {}
    for item in items:
        if item["category"] == "trinket":
            gid = name_to_gid.get(item["name_en"])
            if gid:
                result[item["id"]] = gid
    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Filling trinkets: unlock + stat_changes")
    print("=" * 50)

    items = load_json("items.json")
    trinkets = [i for i in items if i["category"] == "trinket"]
    print(f"Trinkets: {len(trinkets)}")

    # Get game ID mapping
    print("Fetching game ID mapping from wiki.gg...")
    id_map = get_trinket_game_id_map(items)
    print(f"  Mapped {len(id_map)} trinkets to game IDs")

    # Fetch unlock for all trinkets
    results = {}
    done = 0
    no_gid = 0

    def fetch_one(item):
        gid = id_map.get(item["id"])
        if not gid:
            return (item["id"], "初始即可获得", None)
        unlock, _ = fetch_trinket_data(item["id"], gid)
        unlock = cleanup_unlock(unlock, item.get("name_cn", ""))
        return (item["id"], unlock, None)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_one, i): i["id"] for i in trinkets}
        for future in as_completed(futures):
            iid, unlock, _ = future.result()
            results[iid] = unlock
            done += 1
            if done % 40 == 0:
                has = sum(1 for v in results.values() if v != "初始即可获得")
                print(f"  {done}/{len(trinkets)} (has unlock: {has})")

    # Apply unlock
    for item in items:
        if item["id"] in results:
            item["unlock_method"] = results[item["id"]]

    # Extract stat_changes for trinkets
    stat_count = 0
    for item in trinkets:
        effect = item.get("effect", "")
        if not effect:
            continue
        stats = extract_stats(effect)
        if stats:
            item["stat_changes"] = stats
            stat_count += 1
        elif "stat_changes" in item:
            del item["stat_changes"]

    save_json("items.json", items)

    has_u = sum(1 for i in items if i["category"] == "trinket" and i.get("unlock_method") != "初始即可获得")
    print(f"\nDone: unlock={has_u}, stat_changes={stat_count} / {len(trinkets)}")

    # Samples
    print("\nSamples:")
    for i in items:
        if i["id"] in [880, 881, 882, 915, 935, 1007]:
            print(f"  ID {i['id']} {i['name_en']}: unlock={i.get('unlock_method','')[:100]}")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
