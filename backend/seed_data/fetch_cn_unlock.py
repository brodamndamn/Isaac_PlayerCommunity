"""
Fetch Chinese unlock methods from huijiwiki for all passive items.
Uses requests + ThreadPoolExecutor (aiohttp gets 403 from huijiwiki).

Usage: cd backend && python seed_data/fetch_cn_unlock.py
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


def extract_unlock_cn(html: str) -> str:
    """Extract Chinese unlock text from huijiwiki page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    aside = soup.find("aside")
    if aside:
        text = aside.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)

    text = re.sub(r"\s+", " ", text)
    m = re.search(r"解锁条件\s*(.+?)。", text)
    if m:
        unlock = m.group(1).strip()
        if unlock and len(unlock) > 1:
            return unlock

    return "初始即可获得"


def fetch_one(item_id: int) -> tuple[int, str]:
    """Fetch unlock for a single item."""
    cid = f"C{item_id}"
    params = {"action": "parse", "page": cid, "prop": "text", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return (item_id, "")

    if "error" in data:
        return (item_id, "")

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return (item_id, "")

    unlock = extract_unlock_cn(html)
    return (item_id, unlock)


def main():
    print("Fetching Chinese unlock methods from huijiwiki...")
    print("=" * 50)

    items = load_json("items.json")
    passive = [i["id"] for i in items if i["category"] == "passive" and i["id"] <= 732]
    print(f"Passive items: {len(passive)}")

    results: dict[int, str] = {}
    done = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_one, iid): iid for iid in passive}
        for future in as_completed(futures):
            iid, unlock = future.result()
            if unlock:
                results[iid] = unlock
            done += 1
            if done % 50 == 0:
                has = sum(1 for v in results.values() if v != "初始即可获得")
                print(f"  Progress: {done}/{len(passive)} (has unlock: {has})")

    # Update items
    has_unlock = 0
    is_default = 0
    skipped = 0
    for item in items:
        if item["id"] in results:
            unlock = results[item["id"]]
            item["unlock_method"] = unlock
            if unlock == "初始即可获得":
                is_default += 1
            else:
                has_unlock += 1
        else:
            skipped += 1

    save_json("items.json", items)

    print(f"\nResults: has_unlock={has_unlock}, default={is_default}, skipped={skipped}")

    # Show samples
    print("\nSamples:")
    for i in items:
        if i["id"] in [1, 52, 114, 118, 331, 548, 619, 667]:
            print(f"  ID {i['id']} {i['name_en']}: {i.get('unlock_method', '')[:150]}")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
