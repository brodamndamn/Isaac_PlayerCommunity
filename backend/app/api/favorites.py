from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from sqlalchemy import func

from app.models.favorite import Favorite
from app.models.guide import Guide
from app.models.like import Like
from app.models.user import User
from app.schemas.favorite import FavoriteResponse

router = APIRouter(prefix="/api/v1/favorites", tags=["favorites"])


@router.get("")
def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的收藏列表（需登录）。"""
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    total = query.count()
    favs = (
        query.order_by(Favorite.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 批量查询攻略信息
    guide_ids = {f.guide_id for f in favs}
    guides_map = {}
    for g in db.query(Guide.id, Guide.title, Guide.author_id, Guide.category, Guide.cover_image).filter(Guide.id.in_(guide_ids)).all():
        guides_map[g.id] = (g.title, g.author_id, g.category, g.cover_image)
    author_ids = {info[1] for info in guides_map.values()}
    users_map = {
        u.id: (u.username, u.avatar)
        for u in db.query(User.id, User.username, User.avatar).filter(User.id.in_(author_ids)).all()
    }

    # 点赞数 / 收藏数 / 当前用户点赞状态
    like_counts: dict[int, int] = {}
    fav_counts: dict[int, int] = {}
    liked_set: set[int] = set()
    if guide_ids:
        for gid, cnt in db.query(Like.guide_id, func.count()).filter(Like.guide_id.in_(guide_ids)).group_by(Like.guide_id).all():
            like_counts[gid] = cnt
        for gid, cnt in db.query(Favorite.guide_id, func.count()).filter(Favorite.guide_id.in_(guide_ids)).group_by(Favorite.guide_id).all():
            fav_counts[gid] = cnt
        for (gid,) in db.query(Like.guide_id).filter(Like.user_id == current_user.id, Like.guide_id.in_(guide_ids)).all():
            liked_set.add(gid)

    items = []
    for f in favs:
        resp = FavoriteResponse.model_validate(f)
        info = guides_map.get(f.guide_id, ("", 0, "", None))
        uname, av = users_map.get(info[1], ("", None))
        resp.guide_title = info[0]
        resp.guide_author = uname
        resp.guide_author_avatar = av
        resp.guide_category = info[2]
        resp.guide_cover = info[3]
        resp.guide_like_count = like_counts.get(f.guide_id, 0)
        resp.guide_fav_count = fav_counts.get(f.guide_id, 0)
        resp.guide_is_liked = f.guide_id in liked_set
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


@router.post("")
def add_favorite(
    guide_id: int = Query(..., description="要收藏的攻略 ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """收藏攻略（需登录）。同一攻略只能收藏一次。"""
    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.guide_id == guide_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="已经收藏过了")

    fav = Favorite(user_id=current_user.id, guide_id=guide_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)

    return {
        "code": 201,
        "message": "收藏成功",
        "data": FavoriteResponse.model_validate(fav).model_dump(),
    }


@router.delete("/{guide_id}")
def remove_favorite(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消收藏（需登录）。"""
    fav = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id, Favorite.guide_id == guide_id)
        .first()
    )
    if not fav:
        raise HTTPException(status_code=404, detail="尚未收藏该攻略")

    db.delete(fav)
    db.commit()

    return {
        "code": 200,
        "message": "已取消收藏",
        "data": None,
    }
