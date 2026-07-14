"""
Fix item classifications and add missing trinkets (Repentance version).

Step 1: Fix passive/active classifications using wiki.gg category lists
Step 2: Add all trinkets from wiki.gg Trinkets page wikitable
Step 3: Fetch Chinese names from huijiwiki (T-pages for trinkets, C-pages for items)
Step 4: Save and summarize

Usage: cd backend && python seed_data/fix_items.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from bs4 import BeautifulSoup

WIKI_GG = "https://bindingofisaacrebirth.wiki.gg/api.php"
HUIJI = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent


def load_json(name: str):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name: str, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ─── Step 1: Fix classifications ────────────────────────────────────────────

def fix_classifications(items: list) -> list:
    """Use wiki.gg category lists to fix passive/active labels."""
    print("=" * 50)
    print("[Step 1] Fixing item classifications...")

    passive_names = set(load_json("_passive_list.json"))
    active_names = set(load_json("_active_list.json"))

    name_to_item = {i["name_en"]: i for i in items}

    fixes = []
    for name in passive_names:
        if name in name_to_item:
            item = name_to_item[name]
            if item["category"] != "passive":
                fixes.append((item["id"], name, item["category"], "passive"))
                item["category"] = "passive"

    for name in active_names:
        if name in name_to_item:
            item = name_to_item[name]
            if item["category"] != "active":
                fixes.append((item["id"], name, item["category"], "active"))
                item["category"] = "active"

    for iid, name, old, new in fixes:
        print(f"  ID {iid}: {name} ({old} → {new})")
    print(f"  Total fixes: {len(fixes)}")

    passive_1_732 = sum(1 for i in items if i["category"] == "passive" and i["id"] <= 732)
    active_1_732 = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732)
    leftover = sum(1 for i in items if i["category"] == "trinket" and i["id"] <= 732)
    print(f"  Result (1-732): passive={passive_1_732}, active={active_1_732}, leftover-trinket={leftover}")

    if leftover > 0:
        print("  [BUG] Items still marked trinket in 1-732:")
        for i in items:
            if i["category"] == "trinket" and i["id"] <= 732:
                print(f"    ID {i['id']}: {i['name_en']}")

    return items


# ─── Step 2: Add trinkets from wiki.gg Trinkets table ────────────────────────

def fetch_trinkets_table() -> list[dict]:
    """Parse the Trinkets page wikitable and return all trinket data."""
    print("\n" + "=" * 50)
    print("[Step 2] Fetching trinkets from wiki.gg Trinkets page...")

    params = {"action": "parse", "page": "Trinkets", "prop": "text", "format": "json"}
    r = requests.get(WIKI_GG, params=params, headers=HEADERS)
    data = r.json()

    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        print("  ERROR: No wikitables found!")
        return []

    table = tables[0]
    rows = table.find_all("tr")[1:]  # skip header

    trinkets = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue

        # Name
        name_cell = cells[0]
        name_link = name_cell.find("a")
        name_en = name_link.get("title", "").strip() if name_link else name_cell.get_text(strip=True)
        if not name_en:
            continue

        # Game ID (format: 5.350.X)
        id_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        game_id = None
        id_match = re.search(r"5\.350\.(\d+)", id_text)
        if id_match:
            game_id = int(id_match.group(1))

        # Quote
        quote = cells[3].get_text(strip=True) if len(cells) > 3 else ""

        # Description
        description = cells[4].get_text(strip=True) if len(cells) > 4 else ""

        trinkets.append({
            "name_en": name_en,
            "game_id": game_id,
            "quote": quote,
            "description": description,
        })

    print(f"  Parsed {len(trinkets)} trinkets from wikitable")
    return trinkets


def merge_trinkets(items: list, trinkets_data: list[dict]) -> list:
    """Add trinkets to items list with new IDs (after existing max ID)."""
    # Build set of (name, category) for dedup
    existing = {(i["name_en"], i["category"]) for i in items}
    max_id = max(i["id"] for i in items)
    next_id = max_id + 1

    added = 0
    skipped = 0

    for t in trinkets_data:
        name = t["name_en"]
        if (name, "trinket") in existing:
            skipped += 1
            continue

        item = {
            "id": next_id,
            "name_en": name,
            "name_cn": "",
            "category": "trinket",
            "quality": None,
            "description": t["description"],
            "effect": "",
            "unlock_method": "",
            "pick_up_text": t["quote"],
            "recharge_time": None,
            "image_url": "",
            "suitable_characters": None,
            "item_pools": None,
        }
        items.append(item)
        next_id += 1
        added += 1

    print(f"  Added: {added}, Skipped (already exist): {skipped}")
    return items


# ─── Step 3: Chinese translations ────────────────────────────────────────────

def fetch_cn_page(cid: str) -> tuple[str, str]:
    """Fetch Chinese name (displaytitle) and effect from huijiwiki page.
    cid: C{id} for collectibles, T{id} for trinkets.
    Returns (name_cn, effect_cn)."""
    name_cn = ""
    effect_cn = ""

    # Get displaytitle
    params = {"action": "parse", "page": cid, "prop": "displaytitle", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return ("", "")

    title = data.get("parse", {}).get("displaytitle", "")
    if title:
        clean = re.sub(r"<[^>]+>", " ", title)
        clean = re.sub(r"\s+", " ", clean).strip()
        m = re.search(r"[一-鿿㐀-䶿?!？！]+", clean)
        if m:
            name_cn = m.group(0)

    # Get extract for effect
    params2 = {"action": "query", "titles": cid, "prop": "extracts", "explaintext": 1, "format": "json"}
    try:
        r2 = requests.get(HUIJI, params=params2, headers=HEADERS, timeout=20)
        data2 = r2.json()
    except Exception:
        return (name_cn, "")

    for page in data2.get("query", {}).get("pages", {}).values():
        extract = page.get("extract", "")
        if not extract:
            break
        m_start = re.search(r"效果\s*=*\s*\n+", extract)
        if m_start:
            rest = extract[m_start.end():]
            m_end = re.search(r"\n==\s*[^=]+\s*==", rest)
            effect = rest[:m_end.start()] if m_end else rest
            effect_cn = effect.strip()
            effect_cn = effect_cn.replace("\\( ", "").replace(" \\)", "")

    return (name_cn, effect_cn)


def fill_chinese_collectibles(items: list):
    """Fetch Chinese names for collectibles (IDs 1-732) missing them."""
    print("\n" + "=" * 50)
    print("[Step 3a] Chinese names for collectibles...")

    need_ids = [i["id"] for i in items if i["id"] <= 732 and not i.get("name_cn")]
    if not need_ids:
        print("  All collectibles have Chinese names!")
        return items

    print(f"  Missing: {len(need_ids)}")

    done = 0
    updated = 0
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_cn_page, f"C{iid}"): iid for iid in need_ids}
        for future in as_completed(futures):
            iid = futures[future]
            name_cn, effect_cn = future.result()
            done += 1
            if name_cn or effect_cn:
                for item in items:
                    if item["id"] == iid:
                        if name_cn and not item.get("name_cn"):
                            item["name_cn"] = name_cn
                        if effect_cn and not item.get("effect"):
                            item["effect"] = effect_cn
                        updated += 1
                        break
            if done % 20 == 0:
                print(f"    {done}/{len(need_ids)} (updated {updated})")

    still = sum(1 for i in items if i["id"] <= 732 and not i.get("name_cn"))
    print(f"  Done: updated {updated}, still missing: {still}")
    return items


def fill_chinese_trinkets(items: list, trinkets_data: list[dict]):
    """Fetch Chinese names for trinkets."""
    print("\n" + "=" * 50)
    print("[Step 3b] Chinese names for trinkets...")

    # Build name → game_id map
    name_to_gid = {t["name_en"]: t["game_id"] for t in trinkets_data if t["game_id"]}

    new_trinkets = [i for i in items if i["category"] == "trinket" and not i.get("name_cn")]
    if not new_trinkets:
        print("  All trinkets have Chinese names!")
        return items

    # Collect unique game IDs to fetch
    need_gids = set()
    for item in new_trinkets:
        gid = name_to_gid.get(item["name_en"])
        if gid:
            need_gids.add(gid)

    if not need_gids:
        print("  No game ID mapping available, trying T1-T191...")
        need_gids = set(range(1, 192))

    print(f"  Trinkets without Chinese: {len(new_trinkets)} (unique game IDs: {len(need_gids)})")

    # Fetch T-pages
    gid_results: dict[int, tuple[str, str]] = {}
    done = 0
    gid_list = sorted(need_gids)

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_cn_page, f"T{gid}"): gid for gid in gid_list}
        for future in as_completed(futures):
            gid = futures[future]
            name_cn, effect_cn = future.result()
            if name_cn or effect_cn:
                gid_results[gid] = (name_cn, effect_cn)
            done += 1
            if done % 50 == 0:
                print(f"    {done}/{len(gid_list)} (found {len(gid_results)})")

    # Apply results
    updated = 0
    for item in items:
        if item["category"] != "trinket" or item.get("name_cn"):
            continue
        gid = name_to_gid.get(item["name_en"])
        if gid and gid in gid_results:
            name_cn, effect_cn = gid_results[gid]
            if name_cn:
                item["name_cn"] = name_cn
                updated += 1
            if effect_cn and not item["effect"]:
                item["effect"] = effect_cn

    still = sum(1 for i in items if i["category"] == "trinket" and not i.get("name_cn"))
    print(f"  Done: updated {updated}, still missing: {still}")
    return items


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("ISAAC Item Fix Tool — Repentance")
    print("=" * 50)

    items = load_json("items.json")

    # Step 1: Fix classifications
    items = fix_classifications(items)

    # Step 2: Add trinkets
    trinkets_data = fetch_trinkets_table()
    items = merge_trinkets(items, trinkets_data)
    save_json("items.json", items)
    print("  [SAVED] Intermediate items.json")

    # Step 3a: Chinese for collectibles
    items = fill_chinese_collectibles(items)
    save_json("items.json", items)

    # Step 3b: Chinese for trinkets
    items = fill_chinese_trinkets(items, trinkets_data)
    save_json("items.json", items)

    # Final summary
    passive = sum(1 for i in items if i["category"] == "passive" and i["id"] <= 732)
    active = sum(1 for i in items if i["category"] == "active" and i["id"] <= 732)
    trinket = sum(1 for i in items if i["category"] == "trinket")
    card = sum(1 for i in items if i["category"] == "card")
    pill = sum(1 for i in items if i["category"] == "pill")
    no_cn = sum(1 for i in items if not i.get("name_cn"))

    print("\n" + "=" * 50)
    print("FINAL SUMMARY")
    print(f"  Passive  (1-732): {passive}  (target: 548)")
    print(f"  Active   (1-732): {active}   (target: 171)")
    print(f"  Trinkets:          {trinket}  (target: 188)")
    print(f"  Cards:             {card}")
    print(f"  Pills:             {pill}")
    print(f"  Total items:       {len(items)}")
    print(f"  Without CN name:   {no_cn}")
    print()
    print("Next: python seed_data.py   to re-import into database")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
