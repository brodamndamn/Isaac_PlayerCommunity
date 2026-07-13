"""
从 Fandom Wiki Endings 页面提取结局数据，生成 endings.json。

用法：cd backend && python seed_data/fetch_endings.py
输出：seed_data/endings.json
"""
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}


def fetch_endings_page() -> str:
    """从 Wiki API 获取 Endings 页面的 HTML。"""
    params = {"action": "parse", "page": "Endings", "prop": "text", "format": "json"}
    resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()["parse"]["text"]["*"]


def parse_endings(html: str) -> list[dict]:
    """从 HTML 中解析每个结局段落，提取编号、名称和解锁道具。"""
    soup = BeautifulSoup(html, "html.parser")
    endings_raw: list[dict] = []
    current = None

    # 遍历 h3 及其后续的 p 标签
    for tag in soup.find_all(["h3", "p"]):
        if tag.name == "h3":
            text = tag.get_text(strip=True)
            # 匹配 "Ending N (Name)" 或 "Final Ending /Ending N (Name)"
            m = re.match(
                r"(?:Final\s+)?Ending\s*(?:/Ending\s*)?(\d+)?" r"\s*\((.+?)\)",
                text,
            )
            if m or "Epilogue" in text:
                if current:
                    endings_raw.append(current)
                num = int(m.group(1)) if m and m.group(1) else None
                name = m.group(2) if m else text.strip("[]")
                # "Final Ending" 无编号的通常是 The Beast（Repentance 结局 22）
                if num is None and m and "beast" in text.lower():
                    num = 22
                current = {
                    "ending_number": num,
                    "name_en": f"Ending {num}" if num else text.strip("[]"),
                    "name_detail": name,
                    "content": [],
                }
        elif current is not None and tag.name == "p":
            current["content"].append(tag.get_text(" ", strip=True))

    if current:
        endings_raw.append(current)

    return endings_raw


def extract_unlocks(text: str) -> list[str] | None:
    """从段落文本中提取解锁的道具/角色名称。"""
    unlocks: list[str] = []
    patterns = [
        r"unlocks?(?: the (?:item|character|trinket))?\s*['\"]?([A-Z][^.,;!]+?)(?:[,.]|$| and )",
        r"unlocks?\s+([A-Z][^.,;!]+)",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            name = m.group(1).strip()
            # 去除常见干扰
            for prefix in ["the ", "a ", "an "]:
                if name.lower().startswith(prefix):
                    name = name[len(prefix) :]
            if len(name) > 2 and len(name) < 60:
                unlocks.append(name)

    # 常见固定模式
    item_match = re.search(r"unlocks?\s+(?:said\s+)?(?:the\s+)?item[,:]\s*(.+?)(?:[,.]|$)", text, re.IGNORECASE)
    if item_match:
        name = item_match.group(1).strip()
        if name not in unlocks:
            unlocks.append(name)

    return unlocks if unlocks else None


# 手工补充数据：Boss 名称和完成方式（Wiki 段落中没有结构化展示）
# 格式：ending_number -> { boss_name, completion_method, required_character, unlock_method }
# 编号以 Repentance DLC 最终版本为准
MANUAL_DATA: dict[int, dict] = {
    1: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 1 次",
        "name_cn": "结局 1",
    },
    2: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 2 次",
        "name_cn": "结局 2",
    },
    3: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 3 次",
        "name_cn": "结局 3",
    },
    4: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 4 次",
        "name_cn": "结局 4",
    },
    5: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 5 次",
        "name_cn": "结局 5",
    },
    6: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 6 次",
        "name_cn": "结局 6",
    },
    7: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 7 次",
        "name_cn": "结局 7",
    },
    8: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 8 次",
        "name_cn": "结局 8",
    },
    9: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 9 次",
        "name_cn": "结局 9",
    },
    10: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 10 次",
        "name_cn": "结局 10",
    },
    11: {
        "boss_name": "Mom's Heart",
        "completion_method": "击败 Mom's Heart 第 11 次",
        "name_cn": "结局 11",
    },
    12: {
        "boss_name": "Satan",
        "completion_method": "进入 Sheol 并击败 Satan",
        "unlock_method": "击败 Mom's Heart 后选择进入 Sheol",
        "name_cn": "结局 12",
    },
    13: {
        "boss_name": "Isaac",
        "completion_method": "进入 Cathedral 并击败 Isaac",
        "unlock_method": "击败 Mom's Heart 后选择进入 Cathedral",
        "name_cn": "结局 13",
    },
    14: {
        "boss_name": "??? (Blue Baby)",
        "completion_method": "携带 The Polaroid 进入 Chest 并击败 ???",
        "unlock_method": "击败 Isaac 后携带 The Polaroid 进入 Chest",
        "name_cn": "结局 14",
    },
    15: {
        "boss_name": "The Lamb",
        "completion_method": "携带 The Negative 进入 Dark Room 并击败 The Lamb",
        "unlock_method": "击败 Satan 后携带 The Negative 进入 Dark Room",
        "name_cn": "结局 15",
    },
    16: {
        "boss_name": "Mega Satan",
        "completion_method": "在 Chest 或 Dark Room 击败 Mega Satan",
        "unlock_method": "收集两片钥匙碎片，在 Chest/Dark Room 打开金色大门",
        "name_cn": "结局 16",
    },
    17: {
        "boss_name": "Hush",
        "completion_method": "在 ??? 层击败 Hush",
        "unlock_method": "30 分钟内击败 Mom's Heart，进入 Blue Womb",
        "name_cn": "结局 17",
    },
    18: {
        "boss_name": "Ultra Greed",
        "completion_method": "Greed 模式中击败 Ultra Greed",
        "unlock_method": "Greed 模式下通关所有层",
        "name_cn": "结局 18",
    },
    19: {
        "boss_name": "Ultra Greedier",
        "completion_method": "Greedier 模式中击败 Ultra Greedier",
        "unlock_method": "Greedier 模式下通关所有层",
        "name_cn": "结局 19",
    },
    20: {
        "boss_name": "Delirium",
        "completion_method": "在 Void 层击败 Delirium",
        "unlock_method": "击败 Hush 后进入 Void，找到 Delirium 房间",
        "name_cn": "结局 20",
    },
    21: {
        "boss_name": "Mother",
        "completion_method": "在 Corpse II 击败 Mother",
        "unlock_method": "在 Mausoleum 获取 Knife 碎片，进入 Corpse",
        "name_cn": "结局 21",
    },
    22: {
        "boss_name": "The Beast",
        "completion_method": "在 Home 层击败 Dogma 和 The Beast",
        "unlock_method": "使用 Dad's Note 进入 Ascent 路线",
        "name_cn": "结局 22",
    },
}


def build_endings(raw: list[dict]) -> list[dict]:
    """组合 Wiki 数据和手工数据，生成最终结局列表。"""
    endings: list[dict] = []

    for i, entry in enumerate(raw):
        num = entry.get("ending_number")
        if num is None:
            # 跳过 Epilogue
            continue

        manual = MANUAL_DATA.get(num, {})
        full_text = " ".join(entry.get("content", []))
        unlocks = extract_unlocks(full_text)

        ending = {
            "id": num,
            "name_en": entry.get("name_en", f"Ending {num}"),
            "name_cn": manual.get("name_cn", f"结局 {num}"),
            "ending_number": num,
            "completion_method": manual.get("completion_method", ""),
            "unlock_method": manual.get("unlock_method"),
            "required_character": manual.get("required_character"),
            "boss_name": manual.get("boss_name", ""),
            "unlocks": unlocks,
            "image_url": None,
        }
        endings.append(ending)

    return endings


def main():
    print("=" * 50)
    print("ISAAC Ending Data Fetcher")
    print("=" * 50)

    print("\n[1/2] Fetching Endings wiki page...")
    try:
        html = fetch_endings_page()
        print(f"  Got {len(html)} chars of HTML")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)

    print("\n[2/2] Parsing endings + merging manual data...")
    raw = parse_endings(html)
    print(f"  Found {len(raw)} sections (including epilogue)")

    endings = build_endings(raw)
    print(f"  Built {len(endings)} endings")

    output_path = "seed_data/endings.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(endings, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(endings)} endings saved to {output_path}")

    # 列出结局概要
    for e in endings:
        print(f"  #{e['ending_number']:2d}  {e['name_en']:<25s}  Boss: {e['boss_name']}")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
