from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.character import Character
from app.schemas.character import CharacterResponse

router = APIRouter(prefix="/api/v1/characters", tags=["characters"])


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
        "data": CharacterResponse.model_validate(char),
    }
