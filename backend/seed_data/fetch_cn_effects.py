"""
Fetch Chinese effect descriptions from huijiwiki (isaac.huijiwiki.com).
Extracts the '效果' (Effect) section from each item page.

Usage: cd backend && python seed_data/fetch_cn_effects.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

WIKI_API = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}


def fetch_effect(cid: str) -> tuple[int, str]:
    """Fetch effect section for a single C-page. Returns (item_id, effect_text)."""
    params = {"action": "query", "titles": cid, "prop": "extracts", "explaintext": 1, "format": "json"}
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        data = r.json()
    except Exception:
        return (int(cid[1:]), "")

    for page in data.get("query", {}).get("pages", {}).values():
        extract = page.get("extract", "")
        if not extract:
            return (int(cid[1:]), "")

        # 提取"效果"章节：从 `效果 ==` 到下一个 `== X ==` 标题
        m_start = re.search(r"效果\s*=*\s*\n+", extract)
        if not m_start:
            return (int(cid[1:]), "")

        rest = extract[m_start.end():]
        m_end = re.search(r"\n==\s*[^=]+\s*==", rest)
        effect = rest[:m_end.start()] if m_end else rest
        effect = effect.strip()
        # 清理LaTeX数学标记: \( ... \) → 纯文本
        effect = effect.replace("\\( ", "").replace(" \\)", "")
    return (int(cid[1:]), effect)


def main():
    with open("seed_data/items.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    max_id = max(item["id"] for item in items)
    cids = [f"C{i}" for i in range(1, max_id + 1)]

    print(f"Fetching Chinese effect sections for {len(cids)} items...")

    results: dict[int, str] = {}
    done = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_effect, cid): cid for cid in cids}
        for future in as_completed(futures):
            item_id, effect = future.result()
            if effect and len(effect) > 5:
                results[item_id] = effect
            done += 1
            if done % 100 == 0:
                print(f"  Progress: {done}/{len(cids)}  (got {len(results)} effects)")

    updated = 0
    for item in items:
        effect_cn = results.get(item["id"], "")
        if effect_cn:
            item["effect"] = effect_cn
            updated += 1

    with open("seed_data/items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {updated}/{len(items)} items have Chinese effect descriptions")
    print("Next: python seed_data.py   to re-import into database")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Total time: {time.time() - start:.1f}s")
