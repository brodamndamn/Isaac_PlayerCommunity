"""
下载硬币 sprite 到 frontend/public/images/heart/coin.png
用于店主（Keeper）的生命值显示。

用法：cd backend && python seed_data/fetch_coin_image.py
"""
import asyncio
import sys
import io
from pathlib import Path

import aiohttp

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}
OUTPUT = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "heart" / "coin.png"


async def main():
    print(f"Fetching coin image from Fandom Wiki...")

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        # 方法1：直接从 Pickups 页面找 Coin 图片
        params = {"action": "parse", "page": "Pickups", "prop": "text", "format": "json"}
        async with session.get(WIKI_API, params=params) as resp:
            data = await resp.json()

        if "parse" not in data:
            print("ERROR: Pickups page not found")
            return

        from bs4 import BeautifulSoup
        html = data["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")

        # 找所有图片，筛选硬币相关的
        coin_urls = []
        for img in soup.find_all("img"):
            src = img.get("data-src", "") or img.get("src", "")
            alt = (img.get("alt", "") or "").lower()
            if not src or src.startswith("data:"):
                continue
            # 硬币 sprite 通常文件名含 coin，尺寸 32x32 左右
            if "coin" in src.lower() or "coin" in alt:
                width = int(img.get("width", "0") or "0")
                coin_urls.append((width, src, alt))
                print(f"  Found: {src} (alt={alt}, width={width})")

        if not coin_urls:
            # 备选：直接搜索 "Penny" 页面
            print("  No coin images on Pickups page, trying Penny page...")
            params2 = {"action": "parse", "page": "Penny", "prop": "text", "format": "json"}
            async with session.get(WIKI_API, params=params2) as resp:
                data2 = await resp.json()
            if "parse" in data2:
                html2 = data2["parse"]["text"]["*"]
                soup2 = BeautifulSoup(html2, "html.parser")
                for img in soup2.find_all("img"):
                    src = img.get("data-src", "") or img.get("src", "")
                    if not src or src.startswith("data:"):
                        continue
                    width = int(img.get("width", "0") or "0")
                    coin_urls.append((width, src, ""))
                    print(f"  Found: {src} (width={width})")

        if not coin_urls:
            print("ERROR: No coin image found")
            return

        # 选择最合适的：优先 32x32 或最大的
        coin_urls.sort(key=lambda x: x[0], reverse=True)
        best_url = coin_urls[0][1]
        print(f"\n  Best URL: {best_url}")

        # 下载
        async with session.get(best_url) as resp:
            if resp.status == 200:
                content = await resp.read()
                OUTPUT.parent.mkdir(parents=True, exist_ok=True)
                OUTPUT.write_bytes(content)
                print(f"  Saved to {OUTPUT} ({len(content)} bytes)")
            else:
                print(f"  ERROR: HTTP {resp.status}")


if __name__ == "__main__":
    asyncio.run(main())