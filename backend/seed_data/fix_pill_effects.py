"""
Re-fetch ALL pill effects from huijiwiki P-pages.
Only extract the main "使用后：" section, skip "大胶囊" (Horse Pill) synergy.
Also fix item references and English text.

Usage: cd backend && python seed_data/fix_pill_effects.py
"""
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

HUIJI = "https://isaac.huijiwiki.com/api.php"
HEADERS = {"User-Agent": "ISAAC-Community-Scraper/1.0 (personal project)"}

SEED_DIR = Path(__file__).parent


def load_json(name):
    with open(SEED_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(SEED_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_effect(extract: str) -> str:
    """Extract only the main pill effect. Skip '大胶囊' (Horse Pill) section."""
    if not extract:
        return ""

    # Find == 效果 == section
    m = re.search(r"==\s*效果\s*==\s*\n+(.*?)(?=\n==\s*[^=]+\s*==|\Z)", extract, re.DOTALL)
    if not m:
        return ""

    section = m.group(1).strip()

    # Extract the main "使用后：" block, stop at "使用后（大胶囊）"
    m2 = re.search(r"使用后：\s*\n*(.*?)(?=\n使用后（\s*大胶囊|$)", section, re.DOTALL)
    if m2:
        effect = m2.group(1).strip()
    else:
        effect = section

    # If effect is too short/incomplete, try full page parse
    if len(effect) < 5:
        return ""

    # Clean up LaTeX math
    effect = effect.replace('\\(', '').replace('\\)', '')
    effect = effect.replace('\\left\\lfloor', '').replace('\\right\\rfloor', '')
    effect = effect.replace('\\lfloor', '').replace('\\rfloor', '')
    effect = effect.replace('\\left(', '(').replace('\\right)', ')')
    effect = effect.replace('\\left', '').replace('\\right', '')
    effect = effect.replace('\\times', '×')
    effect = effect.replace('\\ge', '≥').replace('\\le', '≤')
    effect = effect.replace('\\max', 'max').replace('\\min', 'min')
    effect = effect.replace('\\%', '%').replace('\\,', '')

    # Subscripts
    effect = re.sub(r'_\{([^}]+)\}', r'\1', effect)

    # Fractions
    for cmd in ['\\dfrac', '\\cfrac', '\\frac']:
        while cmd in effect:
            idx = effect.index(cmd)
            after = effect[idx + len(cmd):]
            if not after.startswith('{'):
                break
            depth = 0; b1 = -1
            for i, ch in enumerate(after):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: b1 = i; break
            if b1 <= 0: break
            x = after[1:b1]
            rest = after[b1 + 1:]
            if not rest.startswith('{'): break
            depth = 0; b2 = -1
            for i, ch in enumerate(rest):
                if ch == '{': depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0: b2 = i; break
            if b2 <= 0: break
            y = rest[1:b2]
            effect = effect[:idx] + f'{x}/{y}' + rest[b2 + 1:]

    effect = re.sub(r'\n{3,}', '\n\n', effect)
    effect = re.sub(r' +', ' ', effect)
    effect = effect.strip()

    # Remove placeholder "获得。" or "获得。" text (wiki data gap)
    if effect in ('获得。', '获得', ''):
        effect = ''

    return effect


def fetch_pill_effect(item_id: int) -> tuple[int, str]:
    """Fetch pill effect from huijiwiki P-page."""
    pid = f"P{item_id - 733}"
    params = {"action": "query", "titles": pid, "prop": "extracts", "explaintext": 1, "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return (item_id, "")

    if "error" in data:
        return (item_id, "")

    for page in data.get("query", {}).get("pages", {}).values():
        extract = page.get("extract", "")
        effect = extract_effect(extract)
        if not effect:
            # Try full page parse
            effect = fetch_pill_effect_full(item_id)
        return (item_id, effect)

    return (item_id, "")


def fetch_pill_effect_full(item_id: int) -> str:
    """Fallback: use action=parse for full page text."""
    from bs4 import BeautifulSoup
    pid = f"P{item_id - 733}"
    params = {"action": "parse", "page": pid, "prop": "text", "format": "json"}
    try:
        r = requests.get(HUIJI, params=params, headers=HEADERS, timeout=20)
        data = r.json()
    except Exception:
        return ""

    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    # Use the same extraction logic
    return extract_effect(text)


# ─── Fix item references ─────────────────────────────────────────────────────

def fix_item_references(effect: str) -> str:
    """Replace '获得 XXX 的效果' with the actual effect description."""
    refs_fix = {
        '思想': '显示所有房间图标',
        '超凡升天': '角色获得飞行效果',
        '弯勺魔术': '泪弹获得追踪效果',
        '撒拉弗': '生成1个炽天使跟班',
        '夜之幽魂': '角色获得飞行效果，泪弹获得穿透效果',
    }
    for ref_name, replacement in refs_fix.items():
        old = f'获得 {ref_name}的效果'
        if old in effect:
            effect = effect.replace(old, replacement)
        old2 = f'获得 {ref_name} 的效果'
        if old2 in effect:
            effect = effect.replace(old2, replacement)
    return effect


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Re-fetching ALL pill effects from huijiwiki...")
    print("=" * 50)

    items = load_json("items.json")
    pills = [i for i in items if i["category"] == "pill"]
    print(f"Pills: {len(pills)}")

    results = {}
    done = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_pill_effect, p["id"]): p["id"] for p in pills}
        for future in as_completed(futures):
            iid, effect = future.result()
            results[iid] = effect
            done += 1
            if done % 15 == 0:
                has = sum(1 for v in results.values() if v)
                print(f"  {done}/{len(pills)} (got effect: {has})")

    # Apply results
    updated = 0
    skipped = 0
    for item in items:
        if item["id"] in results:
            effect = results[item["id"]]
            if effect:
                # Fix item references
                effect = fix_item_references(effect)
                item["effect"] = effect
                updated += 1
            else:
                skipped += 1

    save_json("items.json", items)

    print(f"\nDone: updated {updated}, skipped (no effect) {skipped}")

    # Write samples
    with open(SEED_DIR / "_pills_after.txt", "w", encoding="utf-8") as f:
        for item in items:
            if item["id"] in [733, 734, 735, 737, 746, 756]:
                f.write(f'ID {item["id"]} {item["name_en"]} ({item.get("name_cn","")}):\n')
                f.write(f'  {item.get("effect","")[:300]}\n\n')

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"\nTotal time: {time.time() - start:.1f}s")
