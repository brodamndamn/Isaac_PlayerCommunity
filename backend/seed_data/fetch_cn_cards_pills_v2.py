"""
改进版：从灰机 wiki 按 K/P 编号批量获取卡牌和药丸的中文翻译。

发现：
- 卡牌/符文/魂石在 wiki 用 K 编号（K1-K97）
- 药丸用 P 编号（P0-P49）
- ID 与 K/P 的对应：
  - 药丸 ID 733-782: P0-P49 (P = ID - 733)
  - 塔罗正位 ID 783-804: K1-K22 (K = ID - 782)
  - 塔罗逆位 ID 805-826: K56-K77 (K = ID - 749)
  - 扑克牌 ID 827-834: K23-K30 (K = ID - 804)
  - 特殊卡 ID 835-848: 见 SPECIAL_K_MAP
  - 符文 ID 849-859: 见 RUNE_K_MAP
  - 特殊道具 ID 877-879: 见 MISC_K_MAP
  - 魂石 ID 860-876: K81-K97 (K = ID - 779)

用法：cd backend && python seed_data/fetch_cn_cards_pills_v2.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

WIKI_API = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/2.0 (personal project)"}

# 特殊卡牌：name_en -> K 编号（不遵循 ID 公式的）
SPECIAL_K_MAP = {
    "Joker": "K31",
    "Suicide King": "K46",
    "Queen of Hearts": "K79",
    "Chaos Card": "K42",
    "Huge Growth": "K52",
    "Ancient Recall": "K53",
    "Era Walk": "K54",
    "Credit Card": "K43",
    "Rules Card": "K44",
    "? Card": "K48",
    "A Card Against Humanity": "K45",
    "Get out of Jail Free Card": "K47",
    "Holy Card": "K51",
    "Wild Card": "K80",
}

# 符文：name_en -> K 编号
RUNE_K_MAP = {
    "Rune of Hagalaz": "K32",
    "Rune of Jera": "K33",
    "Rune of Ehwaz": "K34",
    "Rune of Dagaz": "K35",
    "Rune of Ansuz": "K36",
    "Rune of Perthro": "K37",
    "Rune of Berkano": "K38",
    "Rune of Algiz": "K39",
    "Blank Rune": "K40",
    "Black Rune": "K41",
    "Rune Shard": "K55",
}

# 杂项道具（ID 877-879）：name_en -> K 编号
MISC_K_MAP = {
    "Dice Shard": "K49",
    "Emergency Contact": "K50",
    "Cracked Key": "K78",
}


def get_k_or_p_for_id(item_id: int, name_en: str, category: str) -> str | None:
    """根据 ID 和 name_en 计算 K/P 编号。"""
    if category == "pill":
        # 药丸：P = ID - 733
        n = item_id - 733
        if 0 <= n <= 60:
            return f"P{n}"
        return None

    if category == "card":
        # 塔罗正位 783-804: K = ID - 782
        if 783 <= item_id <= 804:
            return f"K{item_id - 782}"
        # 塔罗逆位 805-826: K = ID - 749
        if 805 <= item_id <= 826:
            return f"K{item_id - 749}"
        # 扑克牌 827-834: K = ID - 804
        if 827 <= item_id <= 834:
            return f"K{item_id - 804}"
        # 特殊卡 835-848
        if 835 <= item_id <= 848:
            return SPECIAL_K_MAP.get(name_en)
        # 符文 849-859
        if 849 <= item_id <= 859:
            return RUNE_K_MAP.get(name_en)
        # 魂石 860-876: K = ID - 779
        if 860 <= item_id <= 876:
            return f"K{item_id - 779}"
        # 杂项 877-879
        if 877 <= item_id <= 879:
            return MISC_K_MAP.get(name_en)
    return None


def fetch_page(page_id: str) -> dict:
    """获取页面 displaytitle + 正文文本。返回 {name_cn, effect}。"""
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

    if "error" in data:
        return {}

    result: dict = {}

    # 中文名 — 从 displaytitle 提取
    title_html = data.get("parse", {}).get("displaytitle", "")
    if title_html:
        clean = re.sub(r"<[^>]+>", " ", title_html).strip()
        # 去掉常见的罗马数字前缀 "0-" "I-" "II-" "III-" 等
        clean = re.sub(r"^[IVX]+-", "", clean).strip()
        # 先尝试提取包含 ?! 的连续字符（如 "???的魂石"、"!卡"）
        m = re.search(r"[一-鿿㐀-䶿?!]+", clean)
        if m:
            result["name_cn"] = m.group(0)

    # 中文效果 — 从页面 text 解析
    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return result

    soup = BeautifulSoup(html, "html.parser")

    # 移除脚本/样式
    for tag in soup(["script", "style"]):
        tag.decompose()

    # 三层优先级：
    # 优先级1：含 "使用后" 的段落（游戏机制描述）
    # 优先级2：含 "效果" 等其他关键词的段落
    # 优先级3：最长的中文段落（fallback）
    priority1: list[str] = []
    priority2: list[str] = []
    priority3: list[str] = []

    other_keywords = [
        "效果", "拾取后", "获得", "生成", "掉落", "每当", "如果",
        "发射", "吸收", "造成", "召唤", "提升", "恢复", "增加", "减少",
        "随从", "眼泪", "角色", "自动", "暂时", "永久",
    ]

    for tag in soup.find_all(["p", "li", "dd"]):
        text = tag.get_text(" ", strip=True)
        if not text or len(text) < 6 or len(text) > 800:
            continue
        # 必须包含中文
        if not re.search(r"[一-鿿]", text):
            continue
        # 过滤掉 wiki 元信息（"是一个 X 中加入的 Y"）
        if re.search(r"是一个\s*[一-鿿A-Za-z\d† ]+\s*中加入的", text):
            continue

        if "使用后" in text or "使用时" in text or "使用该" in text:
            priority1.append(text)
        elif any(kw in text for kw in other_keywords):
            priority2.append(text)
        else:
            priority3.append(text)

    for pool in (priority1, priority2, priority3):
        if pool:
            # 取最长
            result["effect"] = max(pool, key=len)
            break

    return result


def main():
    print("=" * 50)
    print("Fetch Chinese for cards/pills via K/P page IDs (v2)")
    print("=" * 50)

    with open("seed_data/cards_pills.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"\nTotal items: {len(items)}")

    # 计算每个 item 的 K/P 编号
    page_map: dict[str, str] = {}  # name_en -> K/P 编号
    skipped: list[str] = []
    for item in items:
        name = item["name_en"]
        page = get_k_or_p_for_id(item["id"], name, item["category"])
        if page:
            page_map[name] = page
        else:
            skipped.append(f"  - ID={item['id']:4d} | {name}")

    print(f"Computed K/P pages for {len(page_map)}/{len(items)} items")
    if skipped:
        print(f"\nSkipped {len(skipped)} items (no mapping):")
        for s in skipped:
            print(s)

    # 批量并发获取页面
    cn_data: dict[str, dict] = {}
    workers = 8
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch_page, page_id): name
            for name, page_id in page_map.items()
        }
        done = 0
        for future in as_completed(futures):
            name = futures[future]
            result = future.result() or {}
            if result.get("name_cn") or result.get("effect"):
                cn_data[name] = result
            done += 1
            if done % 20 == 0:
                print(
                    f"  Fetched {done}/{len(page_map)}  "
                    f"(got CN for {len(cn_data)})"
                )

    print(f"\nGot CN data: {len(cn_data)}/{len(page_map)}")

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

    # 报告
    cards = [i for i in items if i["category"] == "card"]
    pills = [i for i in items if i["category"] == "pill"]

    def has_cn(x):
        cn = (x.get("name_cn") or "").strip()
        return bool(cn) and any("一" <= c <= "鿿" for c in cn)

    def has_cn_eff(x):
        eff = (x.get("effect") or "")
        return any("一" <= c <= "鿿" for c in eff) if eff else False

    print(f"\n[AFTER]")
    print(
        f"  Cards: name {sum(has_cn(i) for i in cards)}/{len(cards)} | "
        f"effect {sum(has_cn_eff(i) for i in cards)}/{len(cards)}"
    )
    print(
        f"  Pills: name {sum(has_cn(i) for i in pills)}/{len(pills)} | "
        f"effect {sum(has_cn_eff(i) for i in pills)}/{len(pills)}"
    )

    # 列出仍未翻译的
    print("\n[REMAINING missing CN name]")
    for i in cards + pills:
        if not has_cn(i):
            print(f"  - ID={i['id']:4d} | {i['name_en']} (cat={i['category']})")
    print("\n[REMAINING missing CN effect]")
    for i in cards + pills:
        if not has_cn_eff(i):
            print(f"  - ID={i['id']:4d} | {i['name_en']} (cat={i['category']})")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
