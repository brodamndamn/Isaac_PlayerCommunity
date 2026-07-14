"""
把 cards_pills.json 中的中文翻译（name_cn / effect）增量同步到数据库。

用法：cd backend && python seed_data/update_cn_cards_pills.py
"""
import json
from pathlib import Path

from app.core.database import SessionLocal
from app.models import Item


def main():
    json_path = Path(__file__).parent / "cards_pills.json"
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    db = SessionLocal()
    try:
        updated_name = 0
        updated_effect = 0
        for data in items:
            item = db.query(Item).filter(Item.id == data["id"]).first()
            if item is None:
                print(f"[WARN] ID={data['id']} not in DB, skip: {data['name_en']}")
                continue
            # 中文名：仅当 JSON 中含中文字符且与 DB 不同时更新
            cn_name = (data.get("name_cn") or "").strip()
            if cn_name and any("一" <= c <= "鿿" for c in cn_name):
                if item.name_cn != cn_name:
                    item.name_cn = cn_name
                    updated_name += 1
            # 中文效果
            cn_eff = data.get("effect") or ""
            if cn_eff and any("一" <= c <= "鿿" for c in cn_eff):
                if item.effect != cn_eff:
                    item.effect = cn_eff
                    updated_effect += 1

        db.commit()

        print(f"[DONE] Updated name_cn: {updated_name}, effect: {updated_effect}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
