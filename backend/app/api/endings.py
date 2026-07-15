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
    enriched = []
    for text in (ending.unlocks or []):
        # Try to match against items by Chinese name
        # Strip parenthetical notes like "（角色）", "（道具）" for lookup
        import re
        lookup = re.sub(r'[（(].+[）)]', '', text).strip()
        item = db.query(Item).filter(Item.name_cn == lookup).first()
        char = db.query(Character).filter(Character.name_cn == lookup).first()

        enriched.append(EnrichedUnlock(
            text=text,
            item_id=item.id if item else None,
            character_id=char.id if char else None,
            image_url=item.image_url if item else None,
        ))

    result = EndingResponse.model_validate(ending)
    result.unlocks_enriched = enriched
    return {
        "code": 200,
        "message": "ok",
        "data": result.model_dump(),
    }
