"""
为每个卡牌 ID 抓取独立 sprite。

策略：对每个卡牌 name_en 试多种 Fandom 文件名模板，找到即下载到 <id>.png。
覆盖范围：所有 card category 的 145 个 ID（ID 783-879 中除卡牌药丸 ID 733-782）。
药丸不参与，由前端用 SVG 渲染。

用法：cd backend && python seed_data/fetch_card_sprites.py
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/2.0"}
IMG_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "items"


def name_candidates(name_en: str) -> list[str]:
    """返回 name_en 的多种可能 Fandom 文件名模板。"""
    n = name_en
    safe = n.replace("'", "").replace(" ", "_")
    no_apos = n.replace("'", "")
    soul_name = n.replace("Soul of ", "")
    rune_name = n.replace("Rune of ", "")
    no_of = n.replace(" of ", "Of")
    return [
        f"Pickup {n} icon.png",
        f"Collectible {n} icon.png",
        f"{n} Icon.png",
        # 扑克牌
        f"Pickup {no_of} icon.png",
        f"Collectible {no_of} icon.png",
        # Soul of XXX
        f"Pickup {soul_name} icon.png",
        # Rune of XXX
        f"Pickup {rune_name} icon.png",
        # 缩略（去除后缀）
        f"Collectible {no_apos} icon.png",
    ]


def find_and_download(session: requests.Session, name_en: str) -> tuple[bytes, str] | None:
    for cand in name_candidates(name_en):
        try:
            r = session.get(
                WIKI_API,
                params={
                    "action": "query",
                    "titles": f"File:{cand}",
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
                if url and size > 50:
                    r2 = session.get(url, headers=HEADERS, timeout=30)
                    if r2.status_code == 200 and len(r2.content) > 50:
                        return (r2.content, cand)
        except Exception:
            continue
    return None


def main():
    print("=" * 50)
    print("Fetch per-card sprites (cards only, no pills)")
    print("=" * 50)

    with open(
        Path(__file__).resolve().parent / "cards_pills.json", "r", encoding="utf-8"
    ) as f:
        items = json.load(f)

    # 只处理 card（不处理 pill，pill 用 SVG）
    cards = [i for i in items if i["category"] == "card"]
    print(f"Total cards to process: {len(cards)}")

    session = requests.Session()
    succeeded = 0
    failed = []
    start = time.time()

    for cnt, item in enumerate(cards):
        iid = item["id"]
        name = item["name_en"]
        result = find_and_download(session, name)
        if result:
            content, src = result
            (IMG_DIR / f"{iid}.png").write_bytes(content)
            succeeded += 1
            if cnt < 5 or cnt % 20 == 0:
                print(f"  [{cnt+1}/{len(cards)}] ID={iid:4d} {name!r}: {len(content)}B via {src!r}")
        else:
            failed.append((iid, name))

        if (cnt + 1) % 50 == 0:
            elapsed = time.time() - start
            print(f"  --- {cnt+1}/{len(cards)} done, OK={succeeded}, FAIL={len(failed)}, {elapsed:.0f}s ---")

    print(f"\n[DONE] success={succeeded}, fail={len(failed)}, time={time.time()-start:.1f}s")
    if failed:
        print("\nFailed items (need manual handling):")
        for iid, name in failed:
            print(f"  ID={iid:4d} {name!r}")


if __name__ == "__main__":
    main()