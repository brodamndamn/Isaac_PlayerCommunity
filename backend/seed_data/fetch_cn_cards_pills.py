"""
从灰机 wiki 抓取卡牌和药丸的中文名 + 中文效果。

用法：cd backend && python seed_data/fetch_cn_cards_pills.py
"""
import json
import re
import time

import requests
from bs4 import BeautifulSoup

WIKI_API = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}


def find_page(name_en: str, prefixes=("K", "P")) -> str | None:
    """搜索英文名，找到 K/P 页面。"""
    search_name = re.sub(r"^[IVX]+ - ", "", name_en).replace("?", "").strip()
    params = {
        "action": "query",
        "list": "search",
        "srsearch": search_name,
        "format": "json",
        "srlimit": 3,
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        data = r.json()
        for p in data.get("query", {}).get("search", []):
            title = p["title"]
            for prefix in prefixes:
                if title.startswith(prefix) and title[1:].isdigit():
                    return title
    except Exception:
        pass
    return None


def parse_page(page_id: str) -> dict:
    """解析 K/P 页面，提取中文名和中文效果。"""
    params = {
        "action": "parse",
        "page": page_id,
        "prop": "text|displaytitle",
        "format": "json",
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        data = r.json()
    except Exception:
        return {}

    result: dict = {}

    # 中文名 — 从 displaytitle
    title_html = data.get("parse", {}).get("displaytitle", "")
    if title_html:
        clean = re.sub(r"<[^>]+>", " ", title_html).strip()
        # 提取中文
        m = re.search(r"[一-鿿㐀-䶿]+", clean)
        if m:
            result["name_cn"] = m.group(0)

    # 中文效果 — 从页面文本
    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return result

    soup = BeautifulSoup(html, "html.parser")

    # 策略：找包含"使用后"或"效果"的段落，取最长的一段
    candidates: list[str] = []
    for tag in soup.find_all(["p", "li"]):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue
        # 过滤导航/链接文本
        if len(text) < 8:
            continue
        if any(
            kw in text
            for kw in ["使用后", "效果", "拾取后", "获得", "生成", "掉落", "每当", "如果", "角色"]
        ):
            candidates.append(text)

    if candidates:
        # 取最长的作为效果描述（过滤掉太短的）
        result["effect"] = max(candidates, key=len)
    else:
        # fallback: 取所有段落中最长的非导航文本
        all_texts = [
            tag.get_text(" ", strip=True)
            for tag in soup.find_all(["p", "li"])
            if len(tag.get_text(" ", strip=True)) > 10
        ]
        if all_texts:
            result["effect"] = max(all_texts, key=len)

    return result


def main():
    print("=" * 50)
    print("Fetch Chinese names + effects from huijiwiki")
    print("=" * 50)

    with open("seed_data/cards_pills.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"\nTotal items: {len(items)}")

    # 找到每个物品的 K/P 页面
    page_map: dict[str, str] = {}
    for i, item in enumerate(items):
        name = item["name_en"]
        page = find_page(name)
        if page:
            page_map[name] = page
        if (i + 1) % 30 == 0:
            print(f"  Search: {i + 1}/{len(items)} (found {len(page_map)})")
        time.sleep(0.3)

    print(f"Found pages: {len(page_map)}/{len(items)}")

    # 解析每个页面
    cn_data: dict[str, dict] = {}
    for i, (name, page) in enumerate(page_map.items()):
        result = parse_page(page)
        if result:
            cn_data[name] = result
        if (i + 1) % 30 == 0:
            print(f"  Parse: {i + 1}/{len(page_map)} (got {len(cn_data)})")
        time.sleep(0.2)

    print(f"Got CN data: {len(cn_data)}")

    # 应用
    updated_name = 0
    updated_effect = 0
    for item in items:
        cn = cn_data.get(item["name_en"], {})
        if cn.get("name_cn"):
            item["name_cn"] = cn["name_cn"]
            updated_name += 1
        if cn.get("effect"):
            item["effect"] = cn["effect"]
            updated_effect += 1

    with open("seed_data/cards_pills.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE]")
    print(f"  CN names:   {updated_name}/{len(items)}")
    print(f"  CN effects: {updated_effect}/{len(items)}")

    # 展示几个
    for item in items[:5]:
        print(f"\n  {item['name_en']}")
        print(f"    CN: {item.get('name_cn', 'N/A')}")
        print(f"    Effect: {(item.get('effect') or '')[:100]}")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
