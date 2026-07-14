"""
Fetch unlock methods for passive items from Fandom wiki.
For items without specific unlock requirements, set "初始即可获得".

Usage: cd backend && python seed_data/fetch_unlock.py
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


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_unlock_from_html(html: str) -> str | None:
    """Extract unlock method from Fandom wiki page HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Method 1: Check infobox for "unlocked by" data attribute
    for attr in soup.find_all(attrs={"data-source": True}):
        key = attr["data-source"]
        if "unlock" in key.lower():
            value_div = attr.find(class_="pi-data-value")
            if value_div:
                text = value_div.get_text(" ", strip=True)
                if text and len(text) > 3:
                    return text

    # Method 2: Find h2/h3 heading containing "unlock" keyword
    for tag in soup.find_all(["h2", "h3"]):
        heading = tag.get_text(strip=True).lower()
        if any(kw in heading for kw in ["unlock", "how to unlock"]):
            content_parts = []
            for sib in tag.find_next_siblings():
                if sib.name in ("h2", "h3"):
                    break
                txt = sib.get_text(" ", strip=True)
                if txt:
                    content_parts.append(txt)
            full = " ".join(content_parts)
            if full and len(full) > 5:
                return full[:400]

    # Method 3: Check for "Unlock" as data-source in portable-infobox
    aside = soup.find("aside", class_="portable-infobox")
    if aside:
        for div in aside.find_all(class_="pi-item"):
            label = div.find(class_="pi-data-label")
            if label and "unlock" in label.get_text().lower():
                value = div.find(class_="pi-data-value")
                if value:
                    text = value.get_text(" ", strip=True)
                    if text and len(text) > 3:
                        return text

    return None


async def fetch_unlock(session: aiohttp.ClientSession, item_id: int, name_en: str, sem: asyncio.Semaphore) -> tuple[int, str]:
    """Fetch unlock method for a single item."""
    async with sem:
        params = {"action": "parse", "page": name_en, "prop": "text", "format": "json"}
        try:
            async with session.get(WIKI_API, params=params) as resp:
                data = await resp.json()
        except Exception:
            return (item_id, "")

        if "error" in data:
            return (item_id, "")

        html = data.get("parse", {}).get("text", {}).get("*", "")
        if not html:
            return (item_id, "")

        unlock = extract_unlock_from_html(html)
        return (item_id, unlock or "初始即可获得")


async def main():
    print("Fetching unlock methods for passive items...")
    print("=" * 50)

    items = load_json("items.json")
    passive = [(i["id"], i["name_en"]) for i in items if i["category"] == "passive" and i["id"] <= 732]
    print(f"Passive items: {len(passive)}")

    sem = asyncio.Semaphore(15)
    connector = aiohttp.TCPConnector(limit=15)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks = [fetch_unlock(session, iid, name, sem) for iid, name in passive]

        done = 0
        results: dict[int, str] = {}
        for coro in asyncio.as_completed(tasks):
            iid, unlock = await coro
            results[iid] = unlock
            done += 1
            if done % 50 == 0:
                has_unlock = sum(1 for v in results.values() if v and v != "初始即可获得")
                print(f"  Progress: {done}/{len(passive)} (need unlock: {has_unlock})")

    # Update items
    updated = 0
    need_unlock = 0
    for item in items:
        if item["id"] in results:
            unlock = results[item["id"]]
            item["unlock_method"] = unlock
            updated += 1
            if unlock != "初始即可获得":
                need_unlock += 1

    save_json("items.json", items)

    print(f"\nDone: updated {updated}, need specific unlock: {need_unlock}")
    print(f"Default (available from start): {updated - need_unlock}")

    # Show samples
    print("\nSample results:")
    for i in items:
        if i["id"] in [1, 12, 68, 118, 182, 548, 619]:
            unlock = i.get("unlock_method", "")[:100]
            print(f"  ID {i['id']} {i['name_en']}: {unlock}")

    print(f"\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\nTotal time: {time.time() - start:.1f}s")
