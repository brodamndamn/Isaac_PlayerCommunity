from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.item import Item
from app.schemas.item import ApiResponse, ItemListData, ItemResponse

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("")
def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    search: str | None = Query(None, description="搜索关键词（名称/描述）"),
    category: str | None = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
):
    """道具列表，支持分页、关键词搜索、分类筛选。"""
    query = db.query(Item)

    if category:
        query = query.filter(Item.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Item.name_en.like(pattern))
            | (Item.name_cn.like(pattern))
            | (Item.description.like(pattern))
        )

    total = query.count()
    items = (
        query.order_by(Item.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": [ItemResponse.model_validate(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    """道具详情。"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="道具不存在")
    return {
        "code": 200,
        "message": "ok",
        "data": ItemResponse.model_validate(item),
    }
