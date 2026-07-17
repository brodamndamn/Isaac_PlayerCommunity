"""把磁盘上角色和结局精灵图批量写入数据库 image_url 字段。

用法：cd backend && PYTHONPATH=. python seed_data/update_character_ending_images.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Character, Ending

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def update_characters(db) -> int:
    img_dir = PROJECT_ROOT / "frontend" / "public" / "images" / "characters"
    updated = 0
    for char in db.query(Character).all():
        # 先查 {id}.png，没有就查 {id}_icon.png
        f = img_dir / f"{char.id}.png"
        if not f.exists():
            f = img_dir / f"{char.id}_icon.png"
        url = f"characters/{f.name}" if f.exists() else None
        if char.image_url != url:
            char.image_url = url
            updated += 1
    db.commit()
    return updated


def update_endings(db) -> int:
    img_dir = PROJECT_ROOT / "frontend" / "public" / "images" / "endings"
    updated = 0
    for ending in db.query(Ending).all():
        f = img_dir / f"{ending.id}.png"
        url = f"endings/{ending.id}.png" if f.exists() else None
        if ending.image_url != url:
            ending.image_url = url
            updated += 1
    db.commit()
    return updated


def main():
    if not PROJECT_ROOT.exists():
        print(f"[ERR] Project root not found: {PROJECT_ROOT}")
        return

    db = SessionLocal()
    try:
        nc = update_characters(db)
        ne = update_endings(db)
        print(f"[OK] Characters updated: {nc}")
        print(f"[OK] Endings updated: {ne}")
    finally:
        db.close()


if __name__ == "__main__":
    main()