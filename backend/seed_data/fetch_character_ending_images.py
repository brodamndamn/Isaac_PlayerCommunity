"""
下载角色立绘和结局 Boss 头像到 frontend/public/images/。

角色图片：frontend/public/images/characters/<id>.png
结局图片：frontend/public/images/endings/<id>.png

用法：cd backend && python seed_data/fetch_character_ending_images.py
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

# 输出目录
CHAR_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "characters"
ENDING_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "endings"

# 角色名到 Wiki 页面标题的映射（部分角色需要特殊处理）
CHARACTER_WIKI_TITLES = {
    "Isaac": "Isaac",
    "Magdalene": "Magdalene",
    "Cain": "Cain",
    "Judas": "Judas",
    "???": "???",
    "Azazel": "Azazel",
    "Eden": "Eden",
    "The Lost": "The Lost",
    "Lilith": "Lilith",
    "Keeper": "Keeper",
    "Apollyon": "Apollyon",
    "The Forgotten": "The Forgotten",
    "Bethany": "Bethany",
    "Jacob and Esau": "Jacob and Esau",
    # 里角色
    "Tainted Isaac": "Tainted Isaac",
    "Tainted Magdalene": "Tainted Magdalene",
    "Tainted Cain": "Tainted Cain",
    "Tainted Judas": "Tainted Judas",
    "Tainted ???": "Tainted ???",
    "Tainted Azazel": "Tainted Azazel",
    "Tainted Eden": "Tainted Eden",
    "Tainted Lost": "Tainted Lost",
    "Tainted Lilith": "Tainted Lilith",
    "Tainted Keeper": "Tainted Keeper",
    "Tainted Apollyon": "Tainted Apollyon",
    "Tainted Forgotten": "Tainted Forgotten",
    "Tainted Bethany": "Tainted Bethany",
    "Tainted Jacob and Esau": "Tainted Jacob and Esau",
    "???": "???",
}

# Boss 名到 Wiki 页面标题的映射（英文和中文都支持）
BOSS_WIKI_TITLES = {
    # 英文名
    "Mom's Heart": "Mom's Heart",
    "Satan": "Satan",
    "Isaac": "Isaac (Boss)",
    "??? (Blue Baby)": "??? (Boss)",
    "The Lamb": "The Lamb",
    "Mega Satan": "Mega Satan",
    "Hush": "Hush",
    "Ultra Greed": "Ultra Greed",
    "Ultra Greedier": "Ultra Greedier",
    "Delirium": "Delirium",
    "Mother": "Mother",
    "The Beast": "The Beast",
    "Dogma": "Dogma",
    "Mom": "Mom",
    # 中文名（endings.json 中的 boss_name）
    "妈妈的心脏": "Mom's Heart",
    "撒但": "Satan",
    "以撒": "Isaac (Boss)",
    "???（小蓝人）": "??? (Boss)",
    "羔羊": "The Lamb",
    "超级撒但": "Mega Satan",
    "死寂": "Hush",
    "究极贪婪": "Ultra Greed",
    "究极大贪婪": "Ultra Greedier",
    "精神错乱": "Delirium",
    "母亲": "Mother",
    "祸兽": "The Beast",
}


async def fetch_page_html(session: aiohttp.ClientSession, title: str) -> str | None:
    """从 Wiki API 获取页面 HTML。"""
    params = {"action": "parse", "page": title, "prop": "text", "format": "json"}
    try:
        async with session.get(WIKI_API, params=params) as resp:
            data = await resp.json()
            if "parse" in data:
                return data["parse"]["text"]["*"]
    except Exception as e:
        print(f"  ERROR fetching {title}: {e}")
    return None


def extract_character_image_url(html: str) -> str | None:
    """从角色页面 HTML 中提取立绘图片 URL（alt='Character image'）。"""
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("aside", class_="portable-infobox")
    if not infobox:
        return None

    # 查找 alt='Character image' 的图片，优先选择较大的（Repentance 版本）
    char_imgs = []
    for img in infobox.find_all("img"):
        alt = img.get("alt", "")
        if "Character image" in alt:
            src = img.get("data-src", "") or img.get("src", "")
            if src and not src.startswith("data:"):
                width = int(img.get("width", "0") or "0")
                char_imgs.append((width, src))

    if char_imgs:
        # 选择最大的图片（通常是最新版本）
        char_imgs.sort(key=lambda x: x[0], reverse=True)
        return char_imgs[0][1]
    return None


def extract_boss_portrait_url(html: str) -> str | None:
    """从 Boss 页面 HTML 中提取头像图片 URL（Boss portrait）。"""
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("aside", class_="portable-infobox")
    if not infobox:
        return None

    # 查找 Boss portrait 图片
    for img in infobox.find_all("img"):
        alt = img.get("alt", "")
        src = img.get("data-src", "") or img.get("src", "")
        if "portrait" in alt.lower() or "portrait" in src.lower():
            if src and not src.startswith("data:"):
                return src

    # 备选：查找较大的图片（270x270 是 Boss 头像的标准尺寸）
    for img in infobox.find_all("img"):
        width = int(img.get("width", "0") or "0")
        height = int(img.get("height", "0") or "0")
        if width >= 200 and height >= 200:
            src = img.get("data-src", "") or img.get("src", "")
            if src and not src.startswith("data:") and "font" not in src.lower():
                return src

    return None


async def download_image(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    filepath: Path,
    url: str,
) -> bool:
    """下载单张图片。"""
    if filepath.exists():
        return True  # 已存在，跳过

    async with sem:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    if len(content) > 500:
                        filepath.write_bytes(content)
                        return True
                return False
        except Exception:
            return False


async def main():
    print("=" * 60)
    print("ISAAC Character & Ending Image Downloader")
    print("=" * 60)

    # 读取角色和结局数据
    seed_dir = Path(__file__).resolve().parent
    with open(seed_dir / "characters.json", "r", encoding="utf-8") as f:
        characters = json.load(f)
    with open(seed_dir / "endings.json", "r", encoding="utf-8") as f:
        endings = json.load(f)

    print(f"\nLoaded {len(characters)} characters, {len(endings)} endings")

    # 确保输出目录存在
    CHAR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ENDING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Phase 1: 获取图片 URL
    print("\n[1/4] Fetching character image URLs...")
    char_urls: dict[int, str] = {}
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for char in characters:
            char_id = char["id"]
            name_en = char["name_en"]
            wiki_title = CHARACTER_WIKI_TITLES.get(name_en, name_en)

            html = await fetch_page_html(session, wiki_title)
            if html:
                url = extract_character_image_url(html)
                if url:
                    char_urls[char_id] = url
                    print(f"  #{char_id:2d} {name_en:<20s} -> found")
                else:
                    print(f"  #{char_id:2d} {name_en:<20s} -> NO image found")
            else:
                print(f"  #{char_id:2d} {name_en:<20s} -> page not found")
            await asyncio.sleep(0.3)  # 避免 API 限流

    print(f"\n  Character URLs found: {len(char_urls)}/{len(characters)}")

    # Phase 2: 获取结局图片 URL
    print("\n[2/4] Fetching ending image URLs...")
    ending_urls: dict[int, str] = {}
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for ending in endings:
            end_id = ending["id"]
            boss_name = ending["boss_name"]
            wiki_title = BOSS_WIKI_TITLES.get(boss_name, boss_name)

            html = await fetch_page_html(session, wiki_title)
            if html:
                url = extract_boss_portrait_url(html)
                if url:
                    ending_urls[end_id] = url
                    print(f"  #{end_id:2d} {boss_name:<20s} -> found")
                else:
                    print(f"  #{end_id:2d} {boss_name:<20s} -> NO image found")
            else:
                print(f"  #{end_id:2d} {boss_name:<20s} -> page not found")
            await asyncio.sleep(0.3)

    print(f"\n  Ending URLs found: {len(ending_urls)}/{len(endings)}")

    # Phase 3: 下载角色图片
    print("\n[3/4] Downloading character images...")
    sem = asyncio.Semaphore(8)
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for char_id, url in char_urls.items():
            filepath = CHAR_OUTPUT_DIR / f"{char_id}.png"
            if not filepath.exists():
                tasks.append((char_id, url, filepath))

        print(f"  To download: {len(tasks)}")
        success = 0
        for char_id, url, filepath in tasks:
            result = await download_image(session, sem, filepath, url)
            if result:
                success += 1
            await asyncio.sleep(0.1)
        print(f"  Downloaded: {success}/{len(tasks)}")

    # Phase 4: 下载结局图片
    print("\n[4/4] Downloading ending images...")
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for end_id, url in ending_urls.items():
            filepath = ENDING_OUTPUT_DIR / f"{end_id}.png"
            if not filepath.exists():
                tasks.append((end_id, url, filepath))

        print(f"  To download: {len(tasks)}")
        success = 0
        for end_id, url, filepath in tasks:
            result = await download_image(session, sem, filepath, url)
            if result:
                success += 1
            await asyncio.sleep(0.1)
        print(f"  Downloaded: {success}/{len(tasks)}")

    # 最终统计
    print("\n" + "=" * 60)
    print("DONE!")
    print(f"  Character images: {len(list(CHAR_OUTPUT_DIR.glob('*.png')))}/{len(characters)}")
    print(f"  Ending images: {len(list(ENDING_OUTPUT_DIR.glob('*.png')))}/{len(endings)}")
    print("\nNext: update DB characters.image_url = 'characters/<id>.png'")
    print("      update DB endings.image_url = 'endings/<id>.png'")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\nTotal time: {time.time() - start:.1f}s")
