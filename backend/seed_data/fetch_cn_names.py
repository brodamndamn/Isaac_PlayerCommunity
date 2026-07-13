"""
Fetch Chinese item names from huijiwiki (isaac.huijiwiki.com),
merge into items.json.

Usage: cd backend && python seed_data/fetch_cn_names.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

WIKI_API = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}


def fetch_cn_name(cid: str) -> tuple[int, str]:
    """Fetch displaytitle for a C-page, return (item_id, name_cn)."""
    params = {"action": "parse", "page": cid, "prop": "displaytitle", "format": "json"}
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        data = r.json()
    except Exception:
        return (int(cid[1:]), "")

    title = data.get("parse", {}).get("displaytitle", "")
    if not title:
        return (int(cid[1:]), "")

    # Extract Chinese name: first CJK character sequence
    clean = re.sub(r"<[^>]+>", " ", title)
    clean = re.sub(r"\s+", " ", clean).strip()
    m = re.search(r"[一-鿿㐀-䶿]+", clean)
    name_cn = m.group(0) if m else ""
    return (int(cid[1:]), name_cn)


def main():
    with open("seed_data/items.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    max_id = max(item["id"] for item in items)
    cids = [f"C{i}" for i in range(1, max_id + 1)]

    print(f"Fetching Chinese names for {len(cids)} items...")

    results: dict[int, str] = {}
    done = 0
    workers = 8

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_cn_name, cid): cid for cid in cids}
        for future in as_completed(futures):
            item_id, name_cn = future.result()
            if name_cn:
                results[item_id] = name_cn
            done += 1
            if done % 100 == 0:
                print(f"  Progress: {done}/{len(cids)}  (found {len(results)} names so far)")

    # Merge into items
    updated = 0
    for item in items:
        cn = results.get(item["id"], "")
        if cn:
            item["name_cn"] = cn
            updated += 1

    with open("seed_data/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {updated}/{len(items)} items now have Chinese names")
    print("Next: python seed_data.py   to re-import into database")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start:.1f}s")
