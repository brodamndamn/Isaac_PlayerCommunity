"""
重试下载角色立绘图片。
"""
import asyncio
import json
import time
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}
CHAR_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "characters"

# 角色名到 Wiki 页面标题的映射
CHARACTER_WIKI_TITLES = {
    "Isaac": "Isaac", "Magdalene": "Magdalene", "Cain": "Cain",
    "Judas": "Judas", "???": "???", "Azazel": "Azazel", "Eden": "Eden",
    "The Lost": "The Lost", "Lilith": "Lilith", "Keeper": "Keeper",
    "Apollyon": "Apollyon", "The Forgotten": "The Forgotten",
    "Bethany": "Bethany", "Jacob & Esau": "Jacob and Esau",
    "Tainted Isaac": "Tainted Isaac", "Tainted Magdalene": "Tainted Magdalene",
    "Tainted Cain": "Tainted Cain", "Tainted Judas": "Tainted Judas",
    "Tainted ???": "Tainted ???", "Tainted Azazel": "Tainted Azazel",
    "Tainted Eden": "Tainted Eden", "Tainted Lost": "Tainted Lost",
    "Tainted Lilith": "Tainted Lilith", "Tainted Keeper": "Tainted Keeper",
    "Tainted Apollyon": "Tainted Apollyon", "Tainted Forgotten": "Tainted Forgotten",
    "Tainted Bethany": "Tainted Bethany", "Tainted Jacob & Esau": "Tainted Jacob and Esau",
}


async def fetch_page_html(session: aiohttp.ClientSession, title: str) -> str | None:
    params = {"action": "parse", "page": title, "prop": "text", "format": "json"}
    try:
        async with session.get(WIKI_API, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            data = await resp.json()
            if "parse" in data:
                return data["parse"]["text"]["*"]
    except Exception as e:
        print(f"  ERROR fetching {title}: {e}")
    return None


def extract_character_image_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("aside", class_="portable-infobox")
    if not infobox:
        return None
    char_imgs = []
    for img in infobox.find_all("img"):
        alt = img.get("alt", "")
        if "Character image" in alt:
            src = img.get("data-src", "") or img.get("src", "")
            if src and not src.startswith("data:"):
                width = int(img.get("width", "0") or "0")
                char_imgs.append((width, src))
    if char_imgs:
        char_imgs.sort(key=lambda x: x[0], reverse=True)
        return char_imgs[0][1]
    return None


async def download_image(session: aiohttp.ClientSession, filepath: Path, url: str) -> bool:
    if filepath.exists() and filepath.stat().st_size > 500:
        return True
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status == 200:
                content = await resp.read()
                if len(content) > 500:
                    filepath.write_bytes(content)
                    return True
    except Exception as e:
        print(f"    Download error: {e}")
    return False


async def main():
    print("Retrying character image downloads...")

    with open(Path(__file__).parent / "characters.json", "r", encoding="utf-8") as f:
        characters = json.load(f)

    CHAR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 找出需要下载的角色
    to_download = []
    for char in characters:
        filepath = CHAR_OUTPUT_DIR / f"{char['id']}.png"
        if not filepath.exists() or filepath.stat().st_size <= 500:
            to_download.append(char)

    print(f"Need to download: {len(to_download)}/{len(characters)}")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        success = 0
        for i, char in enumerate(to_download):
            char_id = char["id"]
            name_en = char["name_en"]
            wiki_title = CHARACTER_WIKI_TITLES.get(name_en, name_en)
            filepath = CHAR_OUTPUT_DIR / f"{char_id}.png"

            print(f"[{i+1}/{len(to_download)}] #{char_id:2d} {name_en}...", end=" ", flush=True)

            html = await fetch_page_html(session, wiki_title)
            if html:
                url = extract_character_image_url(html)
                if url:
                    result = await download_image(session, filepath, url)
                    if result:
                        print("OK")
                        success += 1
                    else:
                        print("DOWNLOAD FAILED")
                else:
                    print("NO IMAGE IN PAGE")
            else:
                print("PAGE NOT FOUND")

            await asyncio.sleep(0.5)  # 增加延迟避免限流

    print(f"\nDone: {success}/{len(to_download)} downloaded")
    print(f"Total character images: {len(list(CHAR_OUTPUT_DIR.glob('*.png')))}")


if __name__ == "__main__":
    asyncio.run(main())
