from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.character import Character
from app.models.item import Item
from app.schemas.character import CharacterResponse, EnrichedStartingItem

router = APIRouter(prefix="/api/v1/characters", tags=["characters"])

BOSS_CN = {
    "Mom": "妈妈",
    "Mom's Heart": "妈妈的心脏",
    "It Lives!": "它还活着！",
    "Isaac": "以撒",
    "Satan": "撒但",
    "The Lamb": "羔羊",
    "???": "小蓝人",
    "Mega Satan": "超级撒但",
    "Hush": "死寂",
    "Ultra Greed": "超级贪婪",
    "Ultra Greedier": "困难贪婪模式",
    "Delirium": "精神错乱",
    "Mother": "母亲",
    "The Beast": "祸兽",
    "Boss Rush": "Boss Rush",
}


def _enrich(char: Character, db: Session) -> dict:
    """给角色附加道具中文名、图片 URL，并翻译解锁条件。"""
    # Enrich starting items
    enriched = []
    for name_en in char.starting_items or []:
        item = db.query(Item).filter(Item.name_en == name_en).first()
        enriched.append(EnrichedStartingItem(
            id=item.id if item else None,
            name_en=name_en,
            name_cn=item.name_cn if item else name_en,
            image_url=item.image_url if item else None,
        ))

    # Translate unlock text (longer phrases first to avoid partial matches)
    unlock = char.unlock_method
    if unlock:
        for en, cn in sorted(BOSS_CN.items(), key=lambda x: -len(x[0])):
            unlock = unlock.replace(en, cn)
        unlock = unlock.replace(" 次", "次")

    result = CharacterResponse.model_validate(char)
    result.starting_items_enriched = enriched
    result.unlock_method = unlock
    return result.model_dump()


@router.get("")
def list_characters(
    page: int = Query(1, ge=1),
    page_size: int = Query(34, ge=1, le=100, alias="page_size"),
    is_tainted: bool | None = Query(None, description="筛选表/里角色"),
    search: str | None = Query(None, description="搜索名称"),
    db: Session = Depends(get_db),
):
    """角色列表。默认返回全部 34 个。"""
    query = db.query(Character)

    if is_tainted is not None:
        query = query.filter(Character.is_tainted == is_tainted)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Character.name_en.like(pattern))
            | (Character.name_cn.like(pattern))
        )

    total = query.count()
    characters = (
        query.order_by(Character.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": [CharacterResponse.model_validate(c) for c in characters],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{char_id}")
def get_character(char_id: int, db: Session = Depends(get_db)):
    """角色详情。"""
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {
        "code": 200,
        "message": "ok",
        "data": _enrich(char, db),
    }

