"""
补全 1-732 范围缺失的道具精灵图。

策略：用 'Collectible <name> icon.png' 文件名模板从 Fandom 拿真 sprite。
之前 fetch_item_images.py 用 pageimages 抓到的全是 indicator 占位图，
这次直接走 File 命名空间，命中率更高。

用法：cd backend && python seed_data/fetch_item_images_fixed.py
"""
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/2.0"}
IMG_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "items"


def find_sprite_url(session: requests.Session, name_en: str) -> tuple[str, int] | None:
    """测试多种文件名模板，返回第一个成功的 (url, size)。"""
    # 处理特殊字符：保留空格（Wiki 用空格），去掉 ()
    name = name_en
    if "(Item)" in name:
        name = name.replace(" (Item)", "").strip()
    if name.startswith("The "):
        # 大多数"The X"用 "TheX" 但有些用 "The X"
        pass
    safe = name.replace("'", "").strip()

    candidates = [
        f"Collectible {name} icon.png",
        f"Pickup {name} icon.png",
        f"{name} icon.png",
        f"Collectible {safe} icon.png",
        # 单词系列（如 Eden's Soul 变成 EdensSoul）
        safe.replace(" ", "") + " icon.png",
    ]

    for c in candidates:
        r = session.get(
            WIKI_API,
            params={
                "action": "query",
                "titles": f"File:{c}",
                "prop": "imageinfo",
                "iiprop": "url|size",
                "format": "json",
            },
            headers=HEADERS,
            timeout=15,
        )
        pages = r.json().get("query", {}).get("pages", {})
        for info in pages.values():
            if "missing" in info:
                continue
            ii = info.get("imageinfo", [{}])[0]
            url = ii.get("url")
            size = ii.get("size", 0)
            if url and size > 30:
                return (url, size)
    return None


def main():
    print("=" * 50)
    print("Fetch missing item sprites (1-732)")
    print("=" * 50)

    with open(
        Path(__file__).resolve().parent / "items.json", "r", encoding="utf-8"
    ) as f:
        items = json.load(f)

    # 当前磁盘已有 sprite ID
    have = set()
    for f in IMG_DIR.iterdir():
        if f.suffix == ".png":
            fid_str = f.stem
            if fid_str.isdigit():
                have.add(int(fid_str))

    missing = [
        i for i in items
        if 1 <= i["id"] <= 732 and i["id"] not in have and i["id"] <= 732
    ]
    print(f"Missing items (1-732): {len(missing)}")

    succeeded = 0
    failed = []
    session = requests.Session()

    start = time.time()
    for cnt, item in enumerate(missing):
        iid = item["id"]
        name = item["name_en"]
        result = find_sprite_url(session, name)
        if not result:
            failed.append((iid, name))
            continue
        url, expected_size = result
        # 下载
        try:
            r = session.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and len(r.content) > 50:
                (IMG_DIR / f"{iid}.png").write_bytes(r.content)
                succeeded += 1
            else:
                failed.append((iid, name))
        except Exception:
            failed.append((iid, name))

        if (cnt + 1) % 20 == 0:
            elapsed = time.time() - start
            print(
                f"  [{cnt + 1}/{len(missing)}] "
                f"OK={succeeded}, FAIL={len(failed)} "
                f"({elapsed:.1f}s)"
            )

    print(f"\n[DONE] success={succeeded}, fail={len(failed)}, time={time.time()-start:.1f}s")
    if failed:
        print("\nFailed items:")
        for iid, name in failed[:20]:
            print(f"  ID={iid:4d} {name!r}")


if __name__ == "__main__":
    main()
