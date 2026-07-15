"""
下载饰品（Trinket）精灵图。

饰品 ID 范围 880-1067，Fandom Wiki 文件名格式：Trinket <Name> icon.png
用法：cd backend && python seed_data/fetch_trinket_images.py
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


def find_trinket_sprite(session: requests.Session, name_en: str) -> tuple[str, int] | None:
    """测试多种文件名模板，返回第一个成功的 (url, size)。"""
    name = name_en
    # 去掉 (Trinket) 后缀
    if "(Trinket)" in name:
        name = name.replace(" (Trinket)", "").strip()
    if "(Rune)" in name:
        name = name.replace(" (Rune)", "").strip()
    safe = name.replace("'", "").strip()

    candidates = [
        f"Trinket {name} icon.png",
        f"Trinket {safe} icon.png",
        f"Trinket {safe.replace(' ', '')} icon.png",
        f"Pickup {name} icon.png",
        f"{name} icon.png",
    ]

    for c in candidates:
        try:
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
        except Exception:
            continue
    return None


def main():
    print("=" * 50)
    print("Fetch trinket sprites (880-1067)")
    print("=" * 50)

    # 从数据库读取饰品数据
    from app.core.database import SessionLocal
    from app.models.item import Item

    db = SessionLocal()
    trinkets = db.query(Item).filter(
        Item.category == "trinket",
        Item.id >= 880,
        Item.id <= 1067,
    ).order_by(Item.id).all()
    db.close()

    print(f"Trinkets in DB: {len(trinkets)}")

    # 磁盘已有的 ID
    have = set()
    for f in IMG_DIR.iterdir():
        if f.suffix == ".png" and f.stem.isdigit():
            fid = int(f.stem)
            if 880 <= fid <= 1067:
                have.add(fid)

    missing = [t for t in trinkets if t.id not in have]
    print(f"Already on disk: {len(have)}, Missing: {len(missing)}")

    if not missing:
        print("All trinket images already downloaded!")
        return

    succeeded = 0
    failed = []
    session = requests.Session()

    start = time.time()
    for cnt, t in enumerate(missing):
        result = find_trinket_sprite(session, t.name_en)
        if not result:
            failed.append((t.id, t.name_en, "no sprite found"))
            continue

        url, expected_size = result
        try:
            r = session.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and len(r.content) > 50:
                (IMG_DIR / f"{t.id}.png").write_bytes(r.content)
                succeeded += 1
            else:
                failed.append((t.id, t.name_en, f"download failed ({r.status_code})"))
        except Exception as e:
            failed.append((t.id, t.name_en, str(e)))

        if (cnt + 1) % 20 == 0:
            elapsed = time.time() - start
            print(f"  [{cnt + 1}/{len(missing)}] OK={succeeded}, FAIL={len(failed)} ({elapsed:.1f}s)")

    print(f"\n[DONE] success={succeeded}, fail={len(failed)}, time={time.time()-start:.1f}s")
    if failed:
        print("\nFailed trinkets:")
        for iid, name, reason in failed:
            print(f"  ID={iid:4d} {name!r} — {reason}")


if __name__ == "__main__":
    main()
