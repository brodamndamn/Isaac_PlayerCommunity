from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.guide import Guide
from app.models.user import User
from app.schemas.guide import GuideCreate, GuideListData, GuideResponse

router = APIRouter(prefix="/api/v1/guides", tags=["guides"])


def _make_response(guide: Guide, author_name: str) -> dict:
    """构建攻略响应（含作者名）。"""
    resp = GuideResponse.model_validate(guide)
    resp.author_name = author_name
    return resp.model_dump()


@router.get("")
def list_guides(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    search: str | None = Query(None, description="搜索关键词（标题/正文）"),
    category: str | None = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
):
    """攻略列表，支持分页、关键词搜索、分类筛选。按发布时间倒序。"""
    query = db.query(Guide)

    if category:
        query = query.filter(Guide.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Guide.title.like(pattern)) | (Guide.content.like(pattern))
        )

    total = query.count()
    guides = (
        query.order_by(Guide.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 批量查询作者名，避免 N+1
    author_ids = {g.author_id for g in guides}
    users = (
        db.query(User.id, User.username)
        .filter(User.id.in_(author_ids))
        .all()
    )
    name_map = {uid: uname for uid, uname in users}

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": [_make_response(g, name_map.get(g.author_id, "")) for g in guides],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{guide_id}")
def get_guide(guide_id: int, db: Session = Depends(get_db)):
    """攻略详情。"""
    guide = db.query(Guide).filter(Guide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="攻略不存在")

    user = db.query(User.id, User.username).filter(User.id == guide.author_id).first()
    author_name = user.username if user else ""

    return {
        "code": 200,
        "message": "ok",
        "data": _make_response(guide, author_name),
    }


@router.post("")
def create_guide(
    body: GuideCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建攻略（需登录）。"""
    guide = Guide(
        title=body.title,
        content=body.content,
        author_id=current_user.id,
        category=body.category,
        related_item_id=body.related_item_id,
        related_character_id=body.related_character_id,
        related_ending_id=body.related_ending_id,
    )
    db.add(guide)
    db.commit()
    db.refresh(guide)

    return {
        "code": 201,
        "message": "发布成功",
        "data": _make_response(guide, current_user.username),
    }


@router.delete("/{guide_id}")
def delete_guide(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除攻略（需登录，仅作者或 admin 可删）。"""
    guide = db.query(Guide).filter(Guide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="攻略不存在")

    if current_user.id != guide.author_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此攻略")

    db.delete(guide)
    db.commit()

    return {
        "code": 200,
        "message": "删除成功",
        "data": None,
    }
