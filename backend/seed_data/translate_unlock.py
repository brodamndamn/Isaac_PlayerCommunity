"""
Translate English unlock conditions to Chinese using pattern matching.
Fetches from huijiwiki where available, falls back to translation table.

Usage: cd backend && python seed_data/translate_unlock.py
"""
import json
import re
from pathlib import Path

SEED_DIR = Path(__file__).parent

# Translation tables
BOSS_CN = {
    "Mom": "妈妈",
    "Mom's Heart": "妈妈的心脏",
    "It Lives!": "它还活着！",
    "It Lives": "它还活着！",
    "Isaac": "以撒",
    "Satan": "撒旦",
    "The Lamb": "羔羊",
    "???": "小蓝人",
    "Mega Satan": "超级撒旦",
    "Hush": "死寂",
    "Ultra Greed": "超级贪婪",
    "Ultra Greedier": "超级贪婪（贪婪模式）",
    "Delirium": "精神错乱",
    "Mother": "母亲",
    "The Beast": "兽",
    "Lokii": "洛基双子",
    "C.H.A.D.": "C.H.A.D.",
    "Gish": "基什",
    "Steven": "史蒂文",
    "Little Horn": "小角",
    "Baby Plum": "小梅子",
    "Hornfel": "霍恩菲尔",
}

CHAR_CN = {
    "Isaac": "以撒",
    "Magdalene": "抹大拉",
    "Cain": "该隐",
    "Judas": "犹大",
    "???": "小蓝人",
    "Eve": "夏娃",
    "Samson": "参孙",
    "Azazel": "阿撒泻勒",
    "Lazarus": "拉撒路",
    "Eden": "伊甸",
    "The Lost": "游魂",
    "Lilith": "莉莉丝",
    "Keeper": "店主",
    "Apollyon": "亚玻伦",
    "The Forgotten": "遗骸",
    "Bethany": "伯大尼",
    "Jacob and Esau": "雅各与以扫",
    "Tainted Isaac": "堕化以撒",
    "Tainted Magdalene": "堕化抹大拉",
    "Tainted Cain": "堕化该隐",
    "Tainted Judas": "堕化犹大",
    "Tainted ???": "堕化小蓝人",
    "Tainted Eve": "堕化夏娃",
    "Tainted Samson": "堕化参孙",
    "Tainted Azazel": "堕化阿撒泻勒",
    "Tainted Lazarus": "堕化拉撒路",
    "Tainted Eden": "堕化伊甸",
    "Tainted Lost": "堕化游魂",
    "Tainted Lilith": "堕化莉莉丝",
    "Tainted Keeper": "堕化店主",
    "Tainted Apollyon": "堕化亚玻伦",
    "Tainted Forgotten": "堕化遗骸",
    "Tainted Bethany": "堕化伯大尼",
    "Tainted Jacob": "堕化雅各",
}

CHALLENGE_CN = {
    "The Family Man": "好爸爸",
    "It's in the Cards": "卡片之道",
    "Waka Waka": "吃豆人",
    "The Host": "寄生宿主",
    "Computer Savvy": "电脑专家",
    "The Guardian": "守护者",
    "Onan's Streak": "俄南的连击",
    "Pong": "乒乓球",
    "Scat Man": "粪Man",
    "Isaac's Awakening": "以撒的觉醒",
    "Baptism by Fire": "火之洗礼",
}

# Common phrase translations
PHRASE_CN = {
    "Defeat": "击败",
    "Complete": "完成",
    "Destroy": "摧毁",
    "Donate": "捐款",
    "Coins to the Donation Machine": "个硬币给捐款机",
    "Use the Blood Donation Machine": "使用献血机",
    "times": "次",
    "Obtain three Yes Mother? items in one run": "在一次游戏中获得 3 个\"是的妈妈？\"道具",
    "Become Guppy": "变成猫套（Guppy）",
    "Become Beelzebub": "变成苍蝇套（Beelzebub）",
    "Beat Chapter": "通过第",
    "without taking damage": "章（无伤）",
    "Complete the Boss Rush as": "使用",
    "Complete Boss Rush as": "使用",
    "完成Boss Rush": "",
    "Pick up 5 familiars in a single run": "在一次游戏中拾取 5 个跟班",
    "Pick up any 2 technology items in a single run": "在一次游戏中拾取任意 2 个科技类道具",
    "Destroy 5 rainbow poops": "摧毁 5 个彩虹便便",
    "Complete 7 Daily Challenges": "完成 7 次每日挑战（触摸奖杯）",
    "Defeat all 5 Harbingers": "击败全部 5 个天启骑士",
    "Defeat an Angel": "击败天使",
    "Sleep in 10 beds": "在 10 张床上睡觉",
    "Enter 6 Shops in one run": "在一次游戏中进入 6 次商店",
    "Collect 10 \"Tears Up\" items or pills in one run": "在一次游戏中收集 10 个\"射速上升\"道具或药丸",
    "Take 25 Deals with the Devil": "进行 25 次恶魔交易",
    "Acquire Blood Clot 10 times": "获得 血块 10 次",
    "Take 25 Angel Rooms items": "获取 25 次天使房道具",
    "Have Isaac die to his own explosion": "让以撒被自己的爆炸炸死（来自 吐根酊、鲍勃的烂头 或 Horf! 药丸）",
    "Use 5 Gulp! pills in one run": "在一次游戏中吞下 5 个 Gulp! 药丸",
    "Spawn three charmed enemies in the same room": "在同一个房间中魅惑 3 个敌人",
    "Acquire Rubber Cement 5 times": "获得 橡胶 cement 5 次",
    "Spend 40+ coins in a single Shop": "在一次商店中花费 40 个以上硬币",
    "Become Guppy": "变成猫套（Guppy）",
    "Become Beelzebub": "变成苍蝇套（Beelzebub）",
    "Haemolacria - Acquire Blood Clot 10 times.": "获得 血块 10 次",
    "Destroy 5 rainbow poops": "摧毁 5 个彩虹便便",
    "Complete 7 Daily Challenges (by touching the trophy at the end)": "完成 7 次每日挑战（触摸奖杯）",
    "Pick up 5 familiars in a single run": "在一次游戏中拾取 5 个跟班",
    "Pick up any 2 technology items in a single run ( Any 2 items that have the 'tech' item tag )": "在一次游戏中拾取任意 2 个科技类道具",
    "Take 25 Deals with the Devil": "进行 25 次恶魔交易",
    "Acquire Blood Clot 10 times": "获得 血块 10 次",
    'Collect 10 "Tears Up" items or pills in one run': "在一次游戏中收集 10 个\"射速上升\"道具或药丸",
    "Take 25 Angel Rooms items": "获取 25 次天使房道具",
    "Enter 6 Shops in one run": "在一次游戏中进入 6 次商店",
    "Sleep in 10 beds": "在 10 张床上睡觉",
    "Use 5 Gulp! pills in one run ( Placebo uses count)": "在一次游戏中吞下 5 个 Gulp! 药丸（Placebo 使用也计入）",
    "Spawn three charmed enemies in the same room": "在同一个房间中魅惑 3 个敌人",
    "Acquire Rubber Cement 5 times": "获得 橡胶水泥 5 次",
    "Defeat Mom's Heart or It Lives! on Hard mode as": "使用",
    "在困难模式下击败 妈妈的心脏 / 它还活着！": "",
    "After breaking Hornfel's minecart, kill him before he can escape": "在破坏霍恩菲尔的矿车后，在他逃跑前杀死他",
    "Earn all": "获得所有",
    "Completion Marks on Hard mode as": "在困难模式下的完成标记，使用",
}


def translate_unlock(text: str) -> str:
    """Translate an English unlock condition to Chinese."""
    if not text or text == "初始即可获得":
        return text

    # Check exact phrase matches first
    if text in PHRASE_CN:
        return PHRASE_CN[text]

    # Pattern 1: "Defeat <Boss> as <Char>"
    m = re.match(r"^Defeat (.+) as (.+)$", text)
    if m:
        boss_en = m.group(1).strip()
        char_en = m.group(2).strip()
        boss_cn = BOSS_CN.get(boss_en, boss_en)
        char_cn = CHAR_CN.get(char_en, char_en)
        return f"使用 {char_cn} 击败 {boss_cn}"

    # Pattern 2: "Defeat <Boss> X times"
    m = re.match(r"^Defeat (.+) (\d+) times?$", text)
    if m:
        boss_en = m.group(1).strip()
        n = m.group(2)
        boss_cn = BOSS_CN.get(boss_en, boss_en)
        return f"击败 {boss_cn} {n} 次"

    # Pattern 3: "Defeat <Boss>"
    m = re.match(r"^Defeat (.+)$", text)
    if m:
        boss_en = m.group(1).strip()
        # Check if it's not "Defeat X as Y" (already handled)
        boss_cn = BOSS_CN.get(boss_en, boss_en)
        return f"击败 {boss_cn}"

    # Pattern 4: "Complete <Challenge> (challenge #N)"
    m = re.match(r"^Complete (.+) \(challenge #(\d+)\)$", text)
    if m:
        challenge_en = m.group(1).strip()
        n = m.group(2)
        challenge_cn = CHALLENGE_CN.get(challenge_en, challenge_en)
        return f"完成挑战 #{n}：{challenge_cn}"

    # Pattern 5: "Donate N Coins to the Donation Machine"
    m = re.match(r"^Donate (\d+) Coins to the Donation Machine$", text)
    if m:
        n = m.group(1)
        return f"向捐款机捐款 {n} 个硬币"

    # Pattern 6: "Complete the Boss Rush as <Char>"
    m = re.match(r"^Complete the Boss Rush as (.+)$", text)
    if m:
        char_en = m.group(1).strip()
        char_cn = CHAR_CN.get(char_en, char_en)
        return f"使用 {char_cn} 完成 Boss Rush"

    # Pattern 7: "Complete Boss Rush as <Char>"
    m = re.match(r"^Complete Boss Rush as (.+)$", text)
    if m:
        char_en = m.group(1).strip()
        char_cn = CHAR_CN.get(char_en, char_en)
        return f"使用 {char_cn} 完成 Boss Rush"

    # Pattern 8: "Beat Chapter N"
    m = re.match(r"^Beat Chapter (\d+)$", text)
    if m:
        n = m.group(1)
        return f"通过第 {n} 章"

    # Pattern 9: "Beat Chapter N without taking damage"
    m = re.match(r"^Beat Chapter (\d+) without taking damage$", text)
    if m:
        n = m.group(1)
        return f"无伤通过第 {n} 章"

    # Pattern 10: "Destroy N Tinted Rocks"
    m = re.match(r"^Destroy (\d+) Tinted Rocks$", text)
    if m:
        n = m.group(1)
        return f"摧毁 {n} 个标记石头"

    # Pattern 11: "Use the Blood Donation Machine N times"
    m = re.match(r"^Use the Blood Donation Machine (\d+) times$", text)
    if m:
        n = m.group(1)
        return f"使用献血机 {n} 次"

    # Pattern 12: "Defeat Mom's Heart or It Lives on Hard mode as X"
    m = re.match(r"^Defeat Mom's Heart or It Lives! on Hard mode as (.+)$", text)
    if m:
        char_en = m.group(1).strip()
        char_cn = CHAR_CN.get(char_en, char_en)
        return f"使用 {char_cn} 在困难模式下击败 妈妈的心脏 / 它还活着！"

    # Pattern 13: "Defeat <Boss> X times" with number
    m = re.match(r"^Defeat (.+) (\d+) times$", text)
    if m:
        boss_en = m.group(1).strip()
        n = m.group(2)
        boss_cn = BOSS_CN.get(boss_en, boss_en)
        return f"击败 {boss_cn} {n} 次"

    # Pattern 14: "Earn all X Completion Marks on Hard mode as Y"
    m = re.match(r"^Earn all .+ Completion Marks on Hard mode as (.+)$", text)
    if m:
        char_en = m.group(1).strip()
        char_cn = CHAR_CN.get(char_en, char_en)
        return f"使用 {char_cn} 在困难模式下获得所有完成标记"

    # Pattern 15: "Complete Chapter N"
    m = re.match(r"^Complete Chapter (\d+)$", text)
    if m:
        return f"完成第 {m.group(1)} 章"

    # Pattern 16: "Defeat an Angel N times"
    m = re.match(r"^Defeat an Angel (\d+) times$", text)
    if m:
        return f"击败天使 {m.group(1)} 次"

    # Fallback: try partial pattern replacements
    result = text
    for en, cn in BOSS_CN.items():
        result = result.replace(en, cn)
    for en, cn in CHAR_CN.items():
        result = result.replace(en, cn)

    # If result changed, it's partially translated
    if result != text:
        return result

    # Can't translate - keep English as fallback
    return text


def main():
    items = []
    with open(SEED_DIR / "items.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    updated = 0
    failed = 0
    for item in items:
        unlock = item.get("unlock_method", "")
        if not unlock or unlock == "初始即可获得":
            continue

        cn = translate_unlock(unlock)
        if cn != unlock:
            item["unlock_method"] = cn
            updated += 1

        # Verify it's now Chinese
        has_chinese = bool(re.search(r"[一-鿿]", cn))
        if not has_chinese and cn != "初始即可获得":
            failed += 1

    with open(SEED_DIR / "items.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"Translated: {updated}, Still non-Chinese: {failed}")

    # Show samples
    for i in items:
        if i["id"] in [1, 52, 94, 114, 182, 331, 548, 619, 667]:
            print(f"  ID {i['id']}: {i.get('unlock_method', '')}")

    if failed > 0:
        print("\nUntranslated conditions:")
        seen = set()
        for i in items:
            u = i.get("unlock_method", "")
            if u and not re.search(r"[一-鿿]", u) and u != "初始即可获得":
                if u not in seen:
                    seen.add(u)
                    print(f"  {u}")

    print("\nNext: python seed_data.py")


if __name__ == "__main__":
    main()
