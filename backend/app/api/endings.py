from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.character import Character
from app.models.ending import Ending
from app.models.item import Item
from app.schemas.ending import EndingResponse, EnrichedUnlock

router = APIRouter(prefix="/api/v1/endings", tags=["endings"])


@router.get("")
def list_endings(
    page: int = Query(1, ge=1),
    page_size: int = Query(22, ge=1, le=100, alias="page_size"),
    search: str | None = Query(None, description="搜索结局名称"),
    db: Session = Depends(get_db),
):
    """结局列表，支持分页和名称搜索。默认返回全部 22 个。"""
    query = db.query(Ending)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Ending.name_en.like(pattern))
            | (Ending.name_cn.like(pattern))
        )

    total = query.count()
    endings = (
        query.order_by(Ending.ending_number)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": [EndingResponse.model_validate(e) for e in endings],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{ending_id}")
def get_ending(ending_id: int, db: Session = Depends(get_db)):
    """结局详情。"""
    ending = db.query(Ending).filter(Ending.id == ending_id).first()
    if not ending:
        raise HTTPException(status_code=404, detail="结局不存在")

    # Enrich unlocks with item/character IDs and image URLs
    import re
    enriched = []
    for text in (ending.unlocks or []):
        item = None
        char = None
        u_type = "unknown"
        label = None

        # Skip section headers
        if text.startswith("以下为") or text.startswith("各角色"):
            enriched.append(EnrichedUnlock(text=text, unlock_type="system", label_cn="说明"))
            continue

        # ── Detect type from SHORT tail marker like "（角色）" ──
        tail = re.search(r'[（(](.{1,8})[）)]\s*$', text)
        if tail:
            m = tail.group(1)
            if '角色' in m: u_type = "character"; label = "角色"
            elif '道具' in m: u_type = "item"; label = "道具"
            elif '成就' in m: u_type = "achievement"; label = "成就"
            elif any(k in m for k in ['路线','解锁','开启','路线']): u_type = "system"; label = "系统"

        if u_type == "unknown" and any(k in text for k in ["解锁", "路线"]):
            u_type = "system"; label = "系统"

        # ── Parse name ──
        lookup = re.sub(r'[（(].+[）)]', '', text).strip()

        # Arrow format: "角色 → 道具名"
        arrow = re.match(r'^(.+?)\s*[→>]\s*(.+)$', lookup)
        if arrow:
            char_name = arrow.group(1).strip()
            item_name = arrow.group(2).strip()
            char = db.query(Character).filter(Character.name_cn == char_name).first()
            item = db.query(Item).filter(Item.name_en == item_name).first()
            if not item:
                item = db.query(Item).filter(Item.name_cn == item_name).first()
            if u_type == "unknown":
                u_type = "item"; label = "道具"
        else:
            # Standard format
            char = db.query(Character).filter(Character.name_cn == lookup).first()
            item = db.query(Item).filter(Item.name_cn == lookup).first()
            # Alias map for abbreviated names
            _ITEM_ALIAS = {'D6': '六面骰'}
            item_lookup = _ITEM_ALIAS.get(lookup, lookup)
            if not item:
                item = db.query(Item).filter(Item.name_en == item_lookup).first()
            if not item:
                item = db.query(Item).filter(Item.name_cn == item_lookup).first()
            if u_type == "character" and not char:
                # Try by English name (e.g. "???" matches character name_en)
                char = db.query(Character).filter(Character.name_en == lookup).first()
            if u_type == "character" and not char:
                name_only = re.sub(r'角色', '', lookup).strip()
                char = db.query(Character).filter(Character.name_cn.like(f"%{name_only}%")).first()

        # ── Enforce type marker ──
        if u_type == "character": item = None
        elif u_type == "item": char = None
        elif item and char:
            char = None  # prefer item when ambiguous

        image_url = (item.image_url if item else None) or (char.image_url if char else None)

        enriched.append(EnrichedUnlock(
            text=text, unlock_type=u_type, label_cn=label,
            item_id=item.id if item else None,
            character_id=char.id if char else None,
            image_url=image_url,
        ))

    result = EndingResponse.model_validate(ending)
    result.unlocks_enriched = enriched
    return {
        "code": 200,
        "message": "ok",
        "data": result.model_dump(),
    }
