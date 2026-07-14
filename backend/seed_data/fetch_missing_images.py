"""
补全缺失的道具和卡牌药丸图片。

策略：
1. 卡牌药丸 (ID 733-879)：从 Fandom 下载共享 sprite 到 _shared/，
   然后把 sprite 内容复制成对应 ID 的 <id>.png 文件
2. 道具 (1-732) 缺失的 168 个：跳过（已确认大部分原来抓的是 indicator 占位图，
   直接重抓意义不大；当前 564 张中大部分是真 32x32 sprite，缺失 ID 用占位块即可）

覆盖规则：
- 塔罗 22 张正位 → tarot_normal.png  (红塔罗)
- 塔罗 22 张逆位 → tarot_reversed.png (棕塔罗)
- 扑克 8 张 → tarot_normal.png fallback
- Joker → joker.png (有独立 sprite)
- Rules Card → rules_card.png
- Chaos Card → chaos_card.png
- 卡片类/Holy/Blank/Joker/QuestionMark/Wild 等 → 各自 sprite 或 fallback 到 tarot
- 符文 → 共享 rune.png 或 fallback 到 tarot_normal
- 魂石 17 张 → soul_stone.png 或各自 sprite
- 药丸 50 种 → 按 polarity 分到 3 个 pill sprite

用法：cd backend && python seed_data/fetch_missing_images.py
"""
import json
import re
import sys
from pathlib import Path

import requests

# 添加 backend 根目录到 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/2.0"}
IMG_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "items"
SHARED_DIR = IMG_DIR / "_shared"

# Fandom 文件名 → 本地保存名的映射
SHARED_FILES: dict[str, str] = {
    # 塔罗
    "Pickup 0 - The Fool icon.png": "tarot_normal.png",
    "Pickup 0 - The Fool? icon.png": "tarot_reversed.png",
    # 扑克牌：选 2 of Hearts（Ace of Spades 之类常被用作通用扑克示意）
    "Pickup 2 of Hearts icon.png": "poker_card.png",
    # 特殊卡
    "Pickup Joker icon.png": "joker.png",
    "Pickup Rules Card icon.png": "rules_card.png",
    "Pickup Chaos Card icon.png": "chaos_card.png",
    # 符文
    "Pickup Blank Rune icon.png": "rune.png",
    # 魂石
    "Pickup Soul of Isaac icon.png": "soul_stone.png",
    # 药丸（3 种用户指定）
    "Pill White Yellow.png": "pill_white_yellow.png",
    "Pill Black White.png": "pill_black_white.png",
    "Pill WhiteWhite.png": "pill_white_white.png",
}

# ID 范围与 sprite 分配的映射
TAROT_NORMAL_IDS = set(range(783, 805))  # 22 张正位
TAROT_REVERSED_IDS = set(range(805, 827))  # 22 张逆位
POKER_IDS = set(range(827, 835))  # 8 张扑克
TRINKET_RUNES_RANGES = (
    set(range(849, 860))  # 9 个符文 (Hagalaz-Rune Shard)
)
SOUL_STONE_IDS = set(range(860, 877))  # 17 个魂石
PILL_IDS = set(range(733, 783))  # 50 种药丸


def download_file(fname: str) -> bytes | None:
    """下载 File:<fname> 的内容。"""
    r = requests.get(
        WIKI_API,
        params={
            "action": "query",
            "titles": f"File:{fname}",
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        },
        headers=HEADERS,
        timeout=20,
    )
    pages = r.json().get("query", {}).get("pages", {})
    for info in pages.values():
        if "missing" in info:
            return None
        url = info.get("imageinfo", [{}])[0].get("url")
        if not url:
            return None
        r2 = requests.get(url, headers=HEADERS, timeout=30)
        if r2.status_code == 200:
            return r2.content
    return None


def write_sprite(save_name: str, data: bytes):
    """保存 sprite 到 _shared/。"""
    SHARED_DIR.mkdir(parents=True, exist_ok=True)
    (SHARED_DIR / save_name).write_bytes(data)


def assign_to_id(item_id: int, sprite_data: bytes):
    """把 sprite 复制到 <id>.png。"""
    (IMG_DIR / f"{item_id}.png").write_bytes(sprite_data)


def main():
    print("=" * 50)
    print("Fetch missing card/pill sprites")
    print("=" * 50)
    SHARED_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: 下载所有共享 sprite
    print("\n[1/3] Downloading shared sprites...")
    sprites: dict[str, bytes] = {}
    for fname, save_name in SHARED_FILES.items():
        path = SHARED_DIR / save_name
        if path.exists() and path.stat().st_size > 50:
            print(f"  [skip] {save_name} (exists, {path.stat().st_size} bytes)")
            sprites[save_name] = path.read_bytes()
            continue
        data = download_file(fname)
        if data:
            write_sprite(save_name, data)
            sprites[save_name] = data
            print(f"  [OK]   {save_name} <- {fname} ({len(data)} bytes)")
        else:
            print(f"  [FAIL] {fname} not found")

    # Step 2: 给每个卡牌 ID 分配 sprite 文件名
    # 根据 ID 范围：
    # 733-782 = 药丸 (50 种)
    # 783-826 = 塔罗 (44 张)
    # 827-834 = 扑克 (8 张)
    # 835-848 = 特殊卡 (14 张，含 Joker、Rules、Chaos 等)
    # 849-859 = 符文 (9+ 张)
    # 860-876 = 魂石 (17 张)
    # 877-879 = 杂项 (Dice Shard/Emergency/Cracked Key)

    print("\n[2/3] Assigning sprites to IDs...")
    id_to_sprite: dict[int, str] = {}

    # 塔罗
    for iid in TAROT_NORMAL_IDS:
        id_to_sprite[iid] = "tarot_normal.png"
    for iid in TAROT_REVERSED_IDS:
        id_to_sprite[iid] = "tarot_reversed.png"

    # 扑克
    for iid in POKER_IDS:
        id_to_sprite[iid] = "poker_card.png"

    # 特殊卡（按 cards_pills.json 中的 name_en 匹配）
    special_map = {
        "Joker": "joker.png",
        "Rules Card": "rules_card.png",
        "Chaos Card": "chaos_card.png",
    }
    # 符文
    rune_map = {
        "Blank Rune": "rune.png",
        "Black Rune": "rune.png",
    }
    # 魂石
    soul_map = {"soul_stone.png"}  # 所有 17 个共用

    # 读取 cards_pills.json 获取 name_en
    cp_json = Path(__file__).resolve().parent / "cards_pills.json"
    with open(cp_json, "r", encoding="utf-8") as f:
        cp_items = json.load(f)

    for item in cp_items:
        name = item["name_en"]
        iid = item["id"]
        # 已分配的跳过
        if iid in id_to_sprite:
            continue
        # 835-848 范围（不在塔罗/扑克/符文/魂石/药丸）
        if 835 <= iid <= 848:
            id_to_sprite[iid] = special_map.get(name, "tarot_normal.png")
            continue
        # 849-859 符文
        if iid in TRINKET_RUNES_RANGES:
            id_to_sprite[iid] = rune_map.get(name, "tarot_normal.png")
            continue
        # 860-876 魂石
        if iid in SOUL_STONE_IDS:
            id_to_sprite[iid] = "soul_stone.png"
            continue
        # 877-879 杂项
        if 877 <= iid <= 879:
            id_to_sprite[iid] = "tarot_normal.png"
            continue

    # 药丸：按 polarity 选 sprite
    # 看 cards_pills.json 中是否有 polarity 字段
    pill_map = {
        "negative": "pill_black_white.png",  # 偏负面
        "positive": "pill_white_yellow.png",  # 偏正面
        "neutral": "pill_white_white.png",    # 中性（白白垂直）
    }
    pill_default = "pill_white_white.png"
    for item in cp_items:
        if item["id"] not in PILL_IDS:
            continue
        polarity = (item.get("polarity") or "").lower()
        sprite = pill_map.get(polarity, pill_default)
        id_to_sprite[item["id"]] = sprite

    print(f"  Assigned {len(id_to_sprite)} IDs to sprites")
    print(f"  Coverage: {len(id_to_sprite)}/{sum(1 for i in cp_items if i['id'] in id_to_sprite or i['id'] in id_to_sprite)}")

    # Step 3: 复制 sprite 到每个 ID 的 .png
    print("\n[3/3] Copying sprites to <id>.png...")
    written = 0
    for iid, sprite_name in id_to_sprite.items():
        data = sprites.get(sprite_name)
        if data is None:
            continue
        assign_to_id(iid, data)
        written += 1

    print(f"  Wrote {written} sprite files")

    # 统计
    total_png = len(list(IMG_DIR.glob("*.png")))
    print(f"\nTotal PNG files in {IMG_DIR}: {total_png}")
    print(f"Shared sprites in {SHARED_DIR}: {len(list(SHARED_DIR.glob('*.png')))}")

    # 显示药丸 polarity 分布
    print("\nPill polarity distribution (for debugging):")
    polarity_count: dict[str, int] = {}
    for item in cp_items:
        if item["id"] in PILL_IDS:
            p = item.get("polarity", "(none)")
            polarity_count[p] = polarity_count.get(p, 0) + 1
    for p, c in sorted(polarity_count.items()):
        print(f"  {p}: {c}")


if __name__ == "__main__":
    main()
