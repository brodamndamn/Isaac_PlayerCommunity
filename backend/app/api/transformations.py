"""套装效果 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.item import Item
from app.models.transformation import Transformation
from app.schemas.transformation import EnrichedItem, TransformationResponse

router = APIRouter(prefix="/api/v1/transformations", tags=["transformations"])


def _enrich(t: Transformation, db: Session) -> dict:
    """给套装效果附加道具中文名和图片 URL。"""
    enriched = []
    for item_id in t.required_items or []:
        item = db.query(Item).filter(Item.id == item_id).first()
        enriched.append(EnrichedItem(
            id=item.id if item else None,
            name_en=item.name_en if item else "",
            name_cn=item.name_cn if item else "",
            image_url=item.image_url if item else None,
        ))
    result = TransformationResponse.model_validate(t)
    result.required_items_enriched = enriched
    if t.required_items:
        result.first_item_id = t.required_items[0]
    return result.model_dump()


@router.get("")
def list_transformations(db: Session = Depends(get_db)):
    """套装效果列表"""
    items = db.query(Transformation).order_by(Transformation.id).all()
    result = []
    for t in items:
        d = TransformationResponse.model_validate(t)
        # 第一个所需道具的 ID，方便前端图片占位符标注
        if t.required_items:
            d.first_item_id = t.required_items[0]
        result.append(d)
    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": result,
            "total": len(result),
        },
    }


@router.get("/{transformation_id}")
def get_transformation(transformation_id: int, db: Session = Depends(get_db)):
    """套装效果详情"""
    t = db.query(Transformation).filter(Transformation.id == transformation_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="套装效果不存在")
    return {
        "code": 200,
        "message": "ok",
        "data": _enrich(t, db),
    }
