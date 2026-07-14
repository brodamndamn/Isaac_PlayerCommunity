"""
从 Fandom Wiki 抓取卡牌和药丸数据，生成 cards_pills.json。

用法：cd backend && python seed_data/fetch_cards_pills.py
输出：seed_data/cards_pills.json
"""
import json
import re
import time

import requests
from bs4 import BeautifulSoup

WIKI_API = "https://bindingofisaacrebirth.fandom.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}


def fetch_page_html(page: str) -> str:
    params = {"action": "parse", "page": page, "prop": "text", "format": "json"}
    r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["parse"]["text"]["*"]


def parse_cards_and_runes(html: str) -> list[dict]:
    """解析 Cards and Runes 页面的 wikitable。"""
    soup = BeautifulSoup(html, "html.parser")

    # 找到 h2/h3 及其后的 table 来确定子类型
    card_subtypes = {
        "Major Arcana": "tarot",
        "Reversed Major Arcana": "tarot_reversed",
        "Playing Cards": "playing",
        "Magic: The Gathering": "playing",
        "Credit Card": "playing",
        "Other Playing Cards": "playing",
        "Card Against Humanity": "playing",
        "Monopoly Card": "playing",
        "Holy Card": "playing",
        "Uno Card": "playing",
        "Left Pointing Runes": "rune",
        "Right Pointing Runes": "rune",
        "Other Runes": "rune",
        "Soul Stones": "soul_stone",
    }

    items: list[dict] = []
    seen_names: set[str] = set()

    # 找所有表格，根据前面的 h3 标题判断子类
    tables = soup.find_all("table", class_="wikitable")
    headings = soup.find_all(["h2", "h3"])

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue
        headers = [th.get_text(strip=True).lower() for th in rows[0].find_all("th")]
        # 跳过 voiceover 表（不含 ID 列）
        if "id" not in headers and "icon" not in headers:
            continue

        for row in rows[1:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            # 第0列可能是空白（reversed cards）或序号
            name_col = 0
            id_col = -1
            for i, h in enumerate(headers):
                if "name" in h:
                    name_col = i
                if "id" in h or h == "":
                    if i > name_col:
                        id_col = i
                        break

            # 简化：通常第1列是名称（Table 0），或第2列（Table 1，有空第一列）
            if len(cells) >= 2:
                name_text = cells[1].get_text(strip=True) if len(cells) > 1 and cells[0].get_text(strip=True) == "" else cells[0].get_text(strip=True)
            else:
                name_text = cells[0].get_text(strip=True)

            # 跳过空行和非道具行
            if not name_text or len(name_text) < 2:
                continue
            if name_text.lower() in ("name", "card", "tarot card"):
                continue
            if name_text in seen_names:
                continue
            seen_names.add(name_text)

            # 找 message/description（通常最后一列）
            desc = ""
            for i in range(len(cells) - 1, -1, -1):
                text = cells[i].get_text(strip=True)
                if len(text) > 10 and len(text) < 500:
                    desc = text
                    break

            items.append(
                {
                    "name_en": name_text,
                    "name_cn": "",
                    "category": "card",
                    "effect": desc,
                    "quality": None,
                }
            )

    return items


def parse_pills(html: str) -> list[dict]:
    """解析 Pills 页面的 wikitable。"""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="wikitable")
    items: list[dict] = []

    if not tables:
        return items

    # 第一个表：ID, Pill, Polarity, Class, Effect, Horse Pill Effect
    table = tables[0]
    for row in table.find_all("tr")[1:]:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        name = cells[1].get_text(strip=True)
        polarity = cells[2].get_text(strip=True)
        pill_class = cells[3].get_text(strip=True)
        effect = cells[4].get_text(strip=True)
        horse_effect = cells[5].get_text(strip=True) if len(cells) > 5 else ""

        if not name:
            continue

        full_effect = effect
        if horse_effect:
            full_effect += f" (马药丸: {horse_effect})"

        items.append(
            {
                "name_en": name,
                "name_cn": "",
                "category": "pill",
                "polarity": polarity,
                "class": pill_class,
                "effect": full_effect,
                "quality": None,
            }
        )

    return items


def main():
    print("=" * 50)
    print("ISAAC Cards & Pills Fetcher")
    print("=" * 50)

    all_items: list[dict] = []

    # 1. Pills
    print("\n[1/2] Fetching Pills...")
    try:
        html = fetch_page_html("Pills")
        pills = parse_pills(html)
        print(f"  Got {len(pills)} pills")
        all_items.extend(pills)
    except Exception as e:
        print(f"  ERROR: {e}")

    time.sleep(1)

    # 2. Cards and Runes
    print("\n[2/2] Fetching Cards and Runes...")
    try:
        html = fetch_page_html("Cards and Runes")
        cards = parse_cards_and_runes(html)
        print(f"  Got {len(cards)} cards/runes")
        all_items.extend(cards)
    except Exception as e:
        print(f"  ERROR: {e}")

    # 分配 ID（从现有最大 ID+1 开始）
    with open("seed_data/items.json", "r", encoding="utf-8") as f:
        existing = json.load(f)
    max_id = max(i["id"] for i in existing)

    for idx, item in enumerate(all_items, start=1):
        item["id"] = max_id + idx
        item.setdefault("description", item.get("effect", ""))
        item.setdefault("image_url", None)
        item.setdefault("unlock_method", None)
        item.setdefault("pick_up_text", None)
        item.setdefault("recharge_time", None)
        item.setdefault("item_pools", None)
        item.setdefault("suitable_characters", None)

    output_path = "seed_data/cards_pills.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(all_items)} items saved to {output_path}")
    print(f"  Pills: {len([i for i in all_items if i['category']=='pill'])}")
    print(f"  Cards: {len([i for i in all_items if i['category']=='card'])}")
    print(f"[NOTE] 中文名 (name_cn) 需后续从灰机 wiki 补充")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
