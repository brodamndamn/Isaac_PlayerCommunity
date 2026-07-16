"""
下载道具池图标从 Fandom Wiki。

策略：每个 pool key 对应一个 Fandom Wiki 文件名，直接通过 File 命名空间拿 URL。
无专用图标的 pool（card_drop/pill_pool/trinket_drop/special/story/beggar）跳过。

用法：cd backend && python seed_data/fetch_pool_images.py
"""
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/2.0"}
IMG_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "pool"

# pool_key → Fandom Wiki 文件名
POOL_FILE_MAP = {
    "angel_room": "Angel Room Icon.png",
    "baby_shop": "Item Pool Baby Shop.png",
    "battery_bum": "Item Pool Battery Bum.png",
    "bomb_bum": "Item Pool Bomb Bum.png",
    "boss": "Boss Room Icon.png",
    "confessional": "Achievement Confessional icon.png",
    "crane_game": "Achievement Crane Game icon.png",
    "curse_room": "Curse Room Icon.png",
    "devil_beggar": "Item Pool Devil Beggar.png",
    "devil_room": "Devil Room Icon.png",
    "golden_chest": "Item Pool Golden Chest.png",
    "key_master": "Item Pool Key Master.png",
    "library": "Library Icon.png",
    "moms_chest": "Item Pool Mom's Chest.png",
    "old_chest": "Item Pool Old Chest.png",
    "planetarium": "Planetarium Icon.png",
    "red_chest": "Item Pool Red Chest.png",
    "rotten_beggar": "Achievement Rotten Beggar icon.png",
    "secret_room": "Secret Room Icon.png",
    "shell_game": "Item Pool Shell Game.png",
    "shop": "Shop Icon.png",
    "slot_machine": "Slot Machine.png",
    "treasure_room": "Treasure Room Icon.png",
    "ultra_secret_room": "Ultra Secret Room Icon.png",
    "wooden_chest": "Item Pool Wooden Chest.png",
}

# 无专用图标的 pool，跳过
SKIP_POOLS = {"beggar", "card_drop", "pill_pool", "trinket_drop", "special", "story"}


def get_file_url(session: requests.Session, filename: str) -> str | None:
    """通过 MediaWiki API 获取文件直链。"""
    r = session.get(
        WIKI_API,
        params={
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
        headers=HEADERS,
        timeout=15,
    )
    pages = r.json().get("query", {}).get("pages", {})
    for info in pages.values():
        if "missing" in info:
            return None
        return info.get("imageinfo", [{}])[0].get("url")
    return None


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    success = 0
    failed = []
    skipped = []

    for pool_key, filename in sorted(POOL_FILE_MAP.items()):
        out_path = IMG_DIR / f"{pool_key}.png"
        if out_path.exists():
            print(f"  SKIP (exists): {pool_key}.png")
            success += 1
            continue

        url = get_file_url(session, filename)
        if not url:
            print(f"  FAIL: {pool_key} → {filename} (not found on wiki)")
            failed.append((pool_key, filename))
            continue

        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 20:
            out_path.write_bytes(resp.content)
            print(f"  OK: {pool_key}.png ({len(resp.content)} bytes)")
            success += 1
        else:
            print(f"  FAIL: {pool_key} → {url} (status {resp.status_code})")
            failed.append((pool_key, filename))

    # 跳过的 pool
    for pool_key in sorted(SKIP_POOLS):
        print(f"  SKIP (no icon): {pool_key}")
        skipped.append(pool_key)

    print(f"\n{'='*50}")
    print(f"Success: {success}/{len(POOL_FILE_MAP)}")
    print(f"Failed: {len(failed)}")
    for key, fn in failed:
        print(f"  {key} → {fn}")
    print(f"Skipped (no icon): {len(skipped)}")
    for key in skipped:
        print(f"  {key}")


if __name__ == "__main__":
    main()