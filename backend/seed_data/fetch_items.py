"""
Fetch Isaac item data from Fandom Wiki API, generate items.json.

Usage: cd backend && python seed_data/fetch_items.py
Output: seed_data/items.json
"""
import asyncio
import json
import re
import sys
import time

import aiohttp
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

# ID range -> category mapping (Isaac community convention)
ID_CATEGORY = {
    range(1, 100): "passive",
    range(100, 200): "active",
    range(200, 300): "trinket",
    range(300, 400): "card",
    range(400, 500): "pill",
}


def infer_category(item_id: int) -> str:
    for r, cat in ID_CATEGORY.items():
        if item_id in r:
            return cat
    return "passive"


async def fetch_items_table(session: aiohttp.ClientSession) -> list[dict]:
    """Fetch the Items page, parse all wikitable rows."""
    params = {"action": "parse", "page": "Items", "prop": "text", "format": "json"}
    async with session.get(WIKI_API, params=params) as resp:
        data = await resp.json()

    html = data["parse"]["text"]["*"]
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        print("ERROR: no wikitables found")
        return []

    items = []
    for table in tables:
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) < 4:
                continue

            # ID
            id_cell = cells[1] if len(cells) > 1 else None
            if not id_cell:
                continue
            id_text = id_cell.get_text(strip=True)
            id_match = re.search(r"(\d{1,3})$", id_text)
            if not id_match:
                continue
            item_id = int(id_match.group(1))

            # Name
            name_link = cells[0].find("a") if cells[0] else None
            name_en = name_link.get("title", "").strip() if name_link else ""
            if not name_en:
                continue

            # Quote
            quote = cells[3].get_text(strip=True) if len(cells) > 3 else ""

            # Description
            description = cells[4].get_text(strip=True) if len(cells) > 4 else ""

            # Quality
            quality = None
            if len(cells) > 5:
                q_text = cells[5].get_text(strip=True)
                q_match = re.search(r"(\d)", q_text)
                if q_match:
                    quality = int(q_match.group(1))

            items.append(
                {
                    "id": item_id,
                    "name_en": name_en,
                    "quote": quote,
                    "description": description,
                    "quality": quality,
                    "category": infer_category(item_id),
                }
            )

    return items


async def fetch_item_detail(
    session: aiohttp.ClientSession, page_name: str, sem: asyncio.Semaphore
) -> dict | None:
    """Fetch a single item's detail page (unlock method, pools, etc.)."""
    async with sem:
        params = {"action": "parse", "page": page_name, "prop": "text", "format": "json"}
        try:
            async with session.get(WIKI_API, params=params) as resp:
                data = await resp.json()
        except Exception:
            return None

        html = data.get("parse", {}).get("text", {}).get("*", "")
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        detail: dict = {}

        for attr in soup.find_all(attrs={"data-source": True}):
            key = attr["data-source"]
            value_div = attr.find(class_="pi-data-value")
            if value_div:
                text = value_div.get_text(" ", strip=True)
                if key == "quote":
                    detail["pick_up_text"] = text
                elif key == "id":
                    detail["id"] = text

        # Try to extract unlock method from page text
        unlock_header = soup.find(
            lambda tag: tag.name in ("h2", "h3") and "unlock" in tag.get_text().lower()
        )
        if unlock_header:
            unlock_content = []
            for sibling in unlock_header.find_next_siblings():
                if sibling.name in ("h2", "h3"):
                    break
                unlock_content.append(sibling.get_text(" ", strip=True))
            detail["unlock_method"] = " ".join(unlock_content)[:500] if unlock_content else None

        return detail if detail else None


async def main():
    print("=" * 50)
    print("ISAAC Item Data Fetcher")
    print("=" * 50)

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        print("\n[1/2] Fetching Items table...")
        items = await fetch_items_table(session)
        print(f"  Got {len(items)} items from tables")

        if not items:
            print("ERROR: No items fetched. Check network or Wiki API.")
            sys.exit(1)

        # Phase 2: fetch detail pages (limited concurrency)
        print(f"\n[2/2] Fetching detail pages (concurrency=5)...")
        sem = asyncio.Semaphore(5)
        tasks = [fetch_item_detail(session, item["name_en"], sem) for item in items]

        done = 0
        for coro in asyncio.as_completed(tasks):
            await coro
            done += 1
            if done % 50 == 0:
                print(f"  Progress: {done}/{len(items)}")

        output_path = "seed_data/items.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        print(f"\n[DONE] {len(items)} items saved to {output_path}")
        print("[NOTE] Chinese names (name_cn) need manual translation from Chinese wiki")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"Total time: {time.time() - start:.1f}s")
