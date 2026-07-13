"""
Fetch Chinese descriptions from huijiwiki (isaac.huijiwiki.com) via extracts API.
Merges into items.json.

Usage: cd backend && python seed_data/fetch_cn_desc.py
"""
import json
import re
import time
from urllib.parse import quote

import requests

WIKI_API = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}
BATCH_SIZE = 20


def fetch_batch_extracts(cids: list[str]) -> dict[str, str]:
    """Fetch intro extracts for a batch of C-pages. Returns {cid: extract_text}."""
    titles = "|".join(cids)
    params = {
        "action": "query",
        "titles": titles,
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1,
        "format": "json",
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
        data = r.json()
    except Exception:
        return {}

    result: dict[str, str] = {}
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "")
        extract = page.get("extract", "")
        if title and extract:
            result[title] = extract.strip()
    return result


def main():
    with open("seed_data/items.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    max_id = max(item["id"] for item in items)
    all_cids = [f"C{i}" for i in range(1, max_id + 1)]

    print(f"Fetching Chinese descriptions for {len(all_cids)} items...")

    # Batch fetch
    all_extracts: dict[str, str] = {}
    batches = [all_cids[i:i + BATCH_SIZE] for i in range(0, len(all_cids), BATCH_SIZE)]

    for i, batch in enumerate(batches):
        extracts = fetch_batch_extracts(batch)
        all_extracts.update(extracts)
        if (i + 1) % 5 == 0:
            print(f"  Batch {i+1}/{len(batches)}  (got {len(all_extracts)} extracts so far)")
        time.sleep(0.3)  # Rate limiting

    # Merge: update description field with Chinese extract
    updated = 0
    for item in items:
        cid = f"C{item['id']}"
        extract = all_extracts.get(cid, "")
        if extract and len(extract) > 10:
            item["description"] = extract
            updated += 1

    with open("seed_data/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {updated}/{len(items)} items have Chinese descriptions")
    print("Next: python seed_data.py   to re-import into database")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start:.1f}s")
