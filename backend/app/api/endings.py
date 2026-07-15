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
    # Manual aliases: unlock text → item name_cn
    _ALIAS_ITEM = {'D6': '六面骰'}
    enriched = []
    for text in (ending.unlocks or []):
        # Strip parenthetical notes like "（角色）", "（道具）" for lookup
        lookup = re.sub(r'[（(].+[）)]', '', text).strip()
        # Determine hint from parenthetical: "角色" → character, "道具" → item
        hint = re.search(r'[（(](.+?)[）)]', text)
        hint_text = hint.group(1) if hint else ""

        # Apply alias if exists
        item_name = _ALIAS_ITEM.get(lookup, lookup)
        item = db.query(Item).filter(Item.name_cn == item_name).first()
        char = db.query(Character).filter(Character.name_cn == lookup).first()

        # If hint says "角色" but no character match, try hint name (e.g. "小蓝人角色" → "小蓝人")
        if not char and '角色' in hint_text:
            hint_lookup = hint_text.replace('角色', '').strip()
            if hint_lookup:
                char = db.query(Character).filter(Character.name_cn == hint_lookup).first()

        # If both match, prefer based on hint
        if item and char:
            if '角色' in hint_text:
                item = None
            elif '道具' in hint_text:
                char = None

        enriched.append(EnrichedUnlock(
            text=text,
            item_id=item.id if item else None,
            character_id=char.id if char else None,
            image_url=(item.image_url if item else None) or (char.image_url if char else None),
        ))

    result = EndingResponse.model_validate(ending)
    result.unlocks_enriched = enriched
    return {
        "code": 200,
        "message": "ok",
        "data": result.model_dump(),
    }
