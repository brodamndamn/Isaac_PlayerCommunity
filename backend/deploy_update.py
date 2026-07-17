#!/usr/bin/env python3
"""一键部署脚本：更新结局、角色、套装、图片数据。"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import SessionLocal
from app.models import Ending, Character, Transformation, Item

db = SessionLocal()

# 1. 更新结局
with open("seed_data/endings.json", encoding="utf-8") as f:
    endings = json.load(f)
for d in endings:
    e = db.query(Ending).filter(Ending.id == d["id"]).first()
    if not e:
        continue
    e.name_cn = d["name_cn"]
    e.completion_method = d.get("completion_method", "")
    e.unlock_method = d.get("unlock_method")
    e.boss_name = d.get("boss_name", "")
    e.unlocks = d.get("unlocks")
db.commit()
print(f"[OK] Endings updated: {len(endings)}")

# 2. 更新角色初始道具
with open("seed_data/characters.json", encoding="utf-8") as f:
    chars = json.load(f)
for c in chars:
    ch = db.query(Character).filter(Character.id == c["id"]).first()
    if ch:
        ch.starting_items = c.get("starting_items", [])
db.commit()
print(f"[OK] Characters updated: {len(chars)}")

# 3. 重新导入套装
db.query(Transformation).delete()
db.commit()
with open("seed_data/transformations.json", encoding="utf-8") as f:
    trans = json.load(f)
count = 0
for t in trans:
    item_ids = []
    for ename in t["required_items"]:
        it = db.query(Item).filter(Item.name_en == ename).first()
        if it:
            item_ids.append(it.id)
    tr = Transformation(
        name_en=t["name_en"], name_cn=t["name_cn"],
        items_needed=t["items_needed"], required_items=item_ids,
        effect=t.get("effect"),
    )
    db.add(tr)
    count += 1
db.commit()
print(f"[OK] Transformations imported: {count}")

# 3.5. 修正道具池名称：赌运气 → 赌博乞丐（游戏房）
for item in db.query(Item).all():
    if item.item_pools:
        new_pools = [p.replace("赌运气", "赌博乞丐（游戏房）") for p in item.item_pools]
        if new_pools != item.item_pools:
            item.item_pools = new_pools
db.commit()
print("[OK] Pool names fixed")

# 4. 同步图片
# 结局图片
img_dir = Path(__file__).resolve().parent.parent / "frontend" / "public" / "images"
for e in db.query(Ending).all():
    f = img_dir / "endings" / f"{e.id}.png"
    url = f"endings/{e.id}.png" if f.exists() else None
    if e.image_url != url:
        e.image_url = url
for c in db.query(Character).all():
    f = img_dir / "characters" / f"{c.id}.png"
    if not f.exists():
        f = img_dir / "characters" / f"{c.id}_icon.png"
    url = f"characters/{f.name}" if f.exists() else None
    if c.image_url != url:
        c.image_url = url
# 道具图片
items_dir = img_dir / "items"
for item in db.query(Item).all():
    f = items_dir / f"{item.id}.png"
    url = f"items/{item.id}.png" if f.exists() else None
    if item.image_url != url:
        item.image_url = url
db.commit()
print("[OK] Images synced")

db.close()
print("\n[DONE] All data updated. Restart backend + rebuild frontend to apply.")
