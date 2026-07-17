"""导入套装数据到数据库。
从 transformations.json 读取，将英文道具名映射为 item ID 后写入 transformations 表。

用法：cd backend && PYTHONPATH=. python seed_data/seed_transformations.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Transformation, Item


def main():
    json_path = Path(__file__).parent / "transformations.json"
    if not json_path.exists():
        print(f"[ERR] {json_path} not found")
        return

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    db = SessionLocal()
    count = 0
    for t in data:
        item_ids = []
        for ename in t["required_items"]:
            it = db.query(Item).filter(Item.name_en == ename).first()
            if it:
                item_ids.append(it.id)
        tr = Transformation(
            name_en=t["name_en"],
            name_cn=t["name_cn"],
            items_needed=t["items_needed"],
            required_items=item_ids,
            effect=t.get("effect"),
        )
        db.add(tr)
        count += 1

    db.commit()
    db.close()
    print(f"[OK] Transformations imported: {count}")


if __name__ == "__main__":
    main()