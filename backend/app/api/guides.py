from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.favorite import Favorite
from app.models.guide import Guide
from app.models.like import Like
from app.models.user import User
from app.schemas.guide import GuideCreate, GuideListData, GuideResponse
from jose import JWTError, jwt
from app.core.config import settings

router = APIRouter(prefix="/api/v1/guides", tags=["guides"])


def _get_optional_user(authorization: str | None, db: Session) -> User | None:
    """尝试从 token 获取当前用户，未登录返回 None。"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(authorization[7:], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.query(User).filter(User.id == int(user_id)).first()
    except JWTError:
        return None

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
    author_id: int | None = Query(None, description="作者 ID 筛选"),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """攻略列表，支持分页、关键词搜索、分类筛选、作者筛选。按发布时间倒序。"""
    query = db.query(Guide)

    if author_id:
        query = query.filter(Guide.author_id == author_id)
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
        db.query(User.id, User.username, User.avatar)
        .filter(User.id.in_(author_ids))
        .all()
    )
    name_map = {uid: uname for uid, uname, _ in users}
    avatar_map = {uid: av for uid, _, av in users}

    # 批量统计点赞数 / 收藏数
    guide_ids = {g.id for g in guides}
    like_counts: dict[int, int] = {}
    fav_counts: dict[int, int] = {}
    if guide_ids:
        for gid, cnt in db.query(Like.guide_id, func.count()).filter(Like.guide_id.in_(guide_ids)).group_by(Like.guide_id).all():
            like_counts[gid] = cnt
        for gid, cnt in db.query(Favorite.guide_id, func.count()).filter(Favorite.guide_id.in_(guide_ids)).group_by(Favorite.guide_id).all():
            fav_counts[gid] = cnt

    # 当前用户的点赞/收藏状态（可选）
    current_user = _get_optional_user(authorization=authorization, db=db)
    liked_set: set[int] = set()
    favorited_set: set[int] = set()
    if current_user and guide_ids:
        for (gid,) in db.query(Like.guide_id).filter(Like.user_id == current_user.id, Like.guide_id.in_(guide_ids)).all():
            liked_set.add(gid)
        for (gid,) in db.query(Favorite.guide_id).filter(Favorite.user_id == current_user.id, Favorite.guide_id.in_(guide_ids)).all():
            favorited_set.add(gid)

    items = []
    for g in guides:
        resp = GuideResponse.model_validate(g)
        resp.author_name = name_map.get(g.author_id, "")
        resp.author_avatar = avatar_map.get(g.author_id)
        resp.like_count = like_counts.get(g.id, 0)
        resp.favorite_count = fav_counts.get(g.id, 0)
        resp.is_liked = g.id in liked_set
        resp.is_favorited = g.id in favorited_set
        items.append(resp.model_dump())

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


@router.get("/{guide_id}")
def get_guide(
    guide_id: int,
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """攻略详情。"""
    guide = db.query(Guide).filter(Guide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="攻略不存在")

    author = db.query(User.id, User.username, User.avatar).filter(User.id == guide.author_id).first()
    author_name = author.username if author else ""
    author_avatar = author.avatar if author else None

    # 计数
    like_count = db.query(func.count()).filter(Like.guide_id == guide_id).scalar() or 0
    fav_count = db.query(func.count()).filter(Favorite.guide_id == guide_id).scalar() or 0
    comment_count = db.query(func.count()).filter(Comment.guide_id == guide_id).scalar() or 0

    # 当前用户状态
    is_liked = False
    is_favorited = False
    current_user = _get_optional_user(authorization, db)
    if current_user:
        is_liked = db.query(Like).filter(Like.user_id == current_user.id, Like.guide_id == guide_id).first() is not None
        is_favorited = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.guide_id == guide_id).first() is not None

    resp = GuideResponse.model_validate(guide)
    resp.author_name = author_name
    resp.author_avatar = author_avatar
    resp.like_count = like_count
    resp.favorite_count = fav_count
    resp.comment_count = comment_count
    resp.is_liked = is_liked
    resp.is_favorited = is_favorited
    return {
        "code": 200,
        "message": "ok",
        "data": resp.model_dump(),
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
        cover_image=body.cover_image,
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
    """删除攻略（需登录，仅作者或 admin 可删）。同时删除关联的评论、收藏、点赞。"""
    guide = db.query(Guide).filter(Guide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="攻略不存在")

    if current_user.id != guide.author_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此攻略")

    # 先删除关联数据（评论的点赞 → 评论 → 收藏 → 点赞）
    comment_ids = [c.id for c in db.query(Comment.id).filter(Comment.guide_id == guide_id).all()]
    if comment_ids:
        db.query(CommentLike).filter(CommentLike.comment_id.in_(comment_ids)).delete()
    db.query(Comment).filter(Comment.guide_id == guide_id).delete()
    db.query(Favorite).filter(Favorite.guide_id == guide_id).delete()
    db.query(Like).filter(Like.guide_id == guide_id).delete()

    db.delete(guide)
    db.commit()

    return {
        "code": 200,
        "message": "删除成功",
        "data": None,
    }
