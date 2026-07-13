"""
种子数据导入脚本。

用法：cd backend && python seed_data.py

数据文件：seed_data/items.json（由 fetch_items.py 从 Wiki 抓取生成）
"""
import json
import sys
from pathlib import Path

from app.core.database import SessionLocal
from app.models import Character, Ending, Item


def seed_items(db) -> int:
    """导入道具种子数据，返回导入条数。"""
    json_path = Path(__file__).parent / "seed_data" / "items.json"
    if not json_path.exists():
        print(f"[SKIP] 未找到 {json_path}，请先运行 seed_data/fetch_items.py 抓取数据")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        items_data = json.load(f)

    count = 0
    for data in items_data:
        # JSON key → 数据库字段映射
        item = Item(
            id=data["id"],
            name_en=data["name_en"],
            name_cn=data.get("name_cn", ""),  # 中文名可能尚未翻译
            category=data.get("category", "passive"),
            quality=data.get("quality"),
            description=data.get("description", ""),
            effect=data.get("effect"),
            unlock_method=data.get("unlock_method"),
            pick_up_text=data.get("quote") or data.get("pick_up_text"),
            recharge_time=data.get("recharge_time"),
            image_url=data.get("image_url"),
            suitable_characters=data.get("suitable_characters"),
            item_pools=data.get("item_pools"),
        )
        db.merge(item)
        count += 1
        # 每 200 条提交一次，避免单次事务过大
        if count % 200 == 0:
            db.commit()

    db.commit()
    return count


def seed_characters(db) -> int:
    """Import character seed data from JSON. Returns count."""
    json_path = Path(__file__).parent / "seed_data" / "characters.json"
    if not json_path.exists():
        print(f"[SKIP] {json_path} not found")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for d in data:
        char = Character(
            id=d["id"],
            name_en=d["name_en"],
            name_cn=d["name_cn"],
            is_tainted=d.get("is_tainted", False),
            base_character_id=d.get("base_character_id"),
            health=d["health"],
            damage=d.get("damage"),
            speed=d.get("speed"),
            tears=d.get("tears"),
            starting_items=d.get("starting_items"),
            unlock_method=d.get("unlock_method"),
            description=d.get("description"),
            suitable_items=d.get("suitable_items"),
            image_url=d.get("image_url"),
        )
        db.merge(char)
        count += 1

    db.commit()
    return count


def seed_endings(db) -> int:
    """Import ending seed data from JSON. Returns count."""
    json_path = Path(__file__).parent / "seed_data" / "endings.json"
    if not json_path.exists():
        print(f"[SKIP] {json_path} not found, run seed_data/fetch_endings.py first")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for d in data:
        ending = Ending(
            id=d["id"],
            name_en=d["name_en"],
            name_cn=d["name_cn"],
            ending_number=d["ending_number"],
            completion_method=d.get("completion_method", ""),
            unlock_method=d.get("unlock_method"),
            required_character=d.get("required_character"),
            boss_name=d.get("boss_name", ""),
            unlocks=d.get("unlocks"),
            image_url=d.get("image_url"),
        )
        db.merge(ending)
        count += 1

    db.commit()
    return count


def main():
    db = SessionLocal()
    try:
        n = seed_items(db)
        print(f"[OK] Items imported: {n}")
        n2 = seed_characters(db)
        print(f"[OK] Characters imported: {n2}")
        n3 = seed_endings(db)
        print(f"[OK] Endings imported: {n3}")
    except Exception as e:
        db.rollback()
        print(f"[FAIL] {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
