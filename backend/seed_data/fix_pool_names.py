"""
Fix pool display names in database: English → Chinese, merge duplicates.

Usage: cd backend && python seed_data/fix_pool_names.py
"""
import sys
import io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 backend 目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.item import Item

# English → Chinese mapping (from fetch_item_pools.py POOL_CN)
POOL_CN = {
    "Baby Shop": "宝宝商店",
    "Battery Bum": "电池乞丐",
    "Rotten Beggar": "腐烂乞丐",
    "Wooden Chest": "木宝箱",
    "Boss Room": "Boss房",
}

# pool key 修正：boss_room → boss（两者都是 Boss房）
KEY_FIX = {
    "boss_room": "boss",
}

def fix_pools(pools: list[str]) -> list[str]:
    result = []
    seen_keys = set()
    for p in pools:
        # 解析 [img:pool/key] display_name
        if not p.startswith("[img:pool/"):
            result.append(p)
            continue

        bracket_end = p.index("]")
        key = p[len("[img:pool/"):bracket_end]
        display = p[bracket_end + 1:].strip()

        # 修正 key（合并重复）
        key = KEY_FIX.get(key, key)

        # 去重
        if key in seen_keys:
            continue
        seen_keys.add(key)

        # 修正显示名
        if display in POOL_CN:
            display = POOL_CN[display]

        result.append(f"[img:pool/{key}] {display}")

    return result


def main():
    db = SessionLocal()
    items = db.query(Item).all()

    updated = 0
    for item in items:
        if not item.item_pools:
            continue
        fixed = fix_pools(item.item_pools)
        if fixed != item.item_pools:
            print(f"ID {item.id} {item.name_en}: {item.item_pools} → {fixed}")
            item.item_pools = fixed
            updated += 1

    db.commit()
    db.close()
    print(f"\nDone: {updated} items updated")


if __name__ == "__main__":
    main()