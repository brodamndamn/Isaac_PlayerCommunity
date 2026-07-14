"""把药丸（category=pill）的 image_url 标记为 polarity 标识符（pill:positive/-/neutral）。前端据此走 SVG 分支。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import Item

# cards_pills.json 中有 polarity 字段
POLARITY_MAP = {
    "+": "positive",
    "-": "negative",
    "N": "neutral",
    "": "neutral",  # fallback
}


def main():
    cp_json = Path(__file__).resolve().parent / "cards_pills.json"
    with open(cp_json, "r", encoding="utf-8") as f:
        items = json.load(f)

    polarity_by_id = {}
    for it in items:
        if it.get("category") != "pill":
            continue
        p = (it.get("polarity") or "").strip()
        polarity_by_id[it["id"]] = POLARITY_MAP.get(p, "neutral")

    db = SessionLocal()
    try:
        updated = 0
        for pill_id, polarity in polarity_by_id.items():
            item = db.query(Item).filter(Item.id == pill_id).first()
            if not item:
                continue
            new_url = f"pill:{polarity}"
            if item.image_url != new_url:
                item.image_url = new_url
                updated += 1
        db.commit()
        # Stats
        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for v in polarity_by_id.values():
            counts[v] += 1
        print(f"Updated {updated} pills: +={counts['positive']} -={counts['negative']} N={counts['neutral']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()