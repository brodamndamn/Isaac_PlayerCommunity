"""把磁盘上合法精灵图同步到数据库 items.image_url。

精灵图定义：文件名 <id>.png，存放在 frontend/public/images/items/
- 单一来源（public/），dist/ 是 Vite build 产物已忽略
- 只设置那些磁盘上确实存在的图为 image_url

用法：cd backend && PYTHONPATH=. python seed_data/update_item_images.py
"""
import os
import sys
from pathlib import Path

# 添加 backend 根目录到 path 以便导入 app.*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Item

IMG_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "images" / "items"


def main():
    if not IMG_DIR.exists():
        print(f"[ERR] {IMG_DIR} not found")
        return

    # 列出所有合法精灵图（纯数字 + png 后缀，且 < 15KB）
    sprite_ids = set()
    for f in IMG_DIR.iterdir():
        if f.suffix != ".png":
            continue
        fid_str = f.stem
        if not fid_str.isdigit():
            continue
        # 只取小文件（< 15KB），过滤掉意外漏网的渲染图
        if f.stat().st_size > 15_000:
            continue
        sprite_ids.add(int(fid_str))

    print(f"Found {len(sprite_ids)} sprite images in {IMG_DIR}")

    db = SessionLocal()
    try:
        updated = 0
        no_img = 0
        for item in db.query(Item).all():
            expected_url = f"items/{item.id}.png" if item.id in sprite_ids else None
            if expected_url != (item.image_url or None):
                item.image_url = expected_url
                updated += 1
            if expected_url is None:
                no_img += 1

        db.commit()
        print(f"Updated {updated} items")
        print(f"Items without image: {no_img}")
        print(f"Items with image: {db.query(Item).filter(Item.image_url.isnot(None)).filter(Item.image_url != '').count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
