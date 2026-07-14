"""
批量下载道具精灵图到 frontend/public/images/items/。

用法：cd backend && python seed_data/fetch_item_images.py
输出：frontend/public/images/items/<item_id>.png
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

import aiohttp

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

# 输出目录（相对于 backend/）
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "items"
BATCH_SIZE = 50  # Wiki API 单次请求最多 50 个 title
CONCURRENCY = 8  # 同时下载数


async def get_image_urls(
    session: aiohttp.ClientSession, titles: list[str]
) -> dict[str, str]:
    """批量获取多个页面的主图 URL。返回 {title: url}。"""
    params = {
        "action": "query",
        "prop": "pageimages",
        "titles": "|".join(titles),
        "piprop": "original",
        "format": "json",
    }
    result: dict[str, str] = {}
    try:
        async with session.get(WIKI_API, params=params) as resp:
            data = await resp.json()
        for pid, info in data.get("query", {}).get("pages", {}).items():
            if "original" in info and "title" in info:
                result[info["title"]] = info["original"]["source"]
    except Exception as e:
        print(f"  API error: {e}")
    return result


async def download_image(
    session: aiohttp.ClientSession,
    sem: asyncio.Semaphore,
    item_id: int,
    url: str,
) -> bool:
    """下载单张图片。"""
    filepath = OUTPUT_DIR / f"{item_id}.png"
    if filepath.exists():
        return True  # 已存在，跳过

    async with sem:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    # 只保存 >500 字节的图片（过滤太小的）
                    if len(content) > 500:
                        filepath.write_bytes(content)
                        return True
                return False
        except Exception:
            return False


async def main():
    print("=" * 50)
    print("ISAAC Item Image Downloader")
    print("=" * 50)

    # 读取 items.json 获取道具名
    json_path = Path(__file__).resolve().parent / "items.json"
    if not json_path.exists():
        print(f"ERROR: {json_path} not found")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)
    print(f"\nLoaded {len(items)} items from items.json")

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 构建 name_en → item_id 映射
    name_to_id: dict[str, int] = {}
    for item in items:
        name_to_id[item["name_en"]] = item["id"]

    item_names = list(name_to_id.keys())

    # Phase 1: 批量获取图片 URL
    print(f"\n[1/3] Fetching image URLs (batches of {BATCH_SIZE})...")
    image_urls: dict[str, str] = {}
    batches = [item_names[i : i + BATCH_SIZE] for i in range(0, len(item_names), BATCH_SIZE)]

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for i, batch in enumerate(batches):
            urls = await get_image_urls(session, batch)
            image_urls.update(urls)
            if (i + 1) % 5 == 0:
                print(f"  Batches: {i + 1}/{len(batches)}  (found {len(image_urls)} URLs so far)")
            await asyncio.sleep(0.5)  # 避免 API 限流

        print(f"  Done: {len(image_urls)}/{len(item_names)} items have images")

        # Phase 2: 检查已下载
        existing = set()
        for f in OUTPUT_DIR.iterdir():
            if f.suffix == ".png":
                try:
                    existing.add(int(f.stem))
                except ValueError:
                    pass

        to_download: list[tuple[int, str]] = []
        skipped = 0
        for name, url in image_urls.items():
            item_id = name_to_id.get(name)
            if item_id is None:
                continue
            if item_id in existing:
                skipped += 1
            else:
                to_download.append((item_id, url))

        print(f"\n[2/3] Downloading images...")
        print(f"  Already have: {skipped}")
        print(f"  To download:  {len(to_download)}")
        print(f"  Concurrency:  {CONCURRENCY}")

        # Phase 3: 下载
        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = [download_image(session, sem, iid, url) for iid, url in to_download]

        done = 0
        success = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            done += 1
            if result:
                success += 1
            if done % 100 == 0:
                print(f"  Progress: {done}/{len(to_download)}  (success: {success})")

        print(f"  Done: {success}/{len(to_download)} downloaded successfully")

    # 最终统计
    total_files = len(list(OUTPUT_DIR.glob("*.png")))
    print(f"\n[3/3] Complete!")
    print(f"  Total images in {OUTPUT_DIR}: {total_files}")
    missing = len(items) - total_files
    if missing > 0:
        print(f"  Missing: {missing} items (may not have wiki images)")
    print(f"  Next: update DB items.image_url = 'items/<id>.png'")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\nTotal time: {time.time() - start:.1f}s")
