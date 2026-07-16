from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.like import Like
from app.models.user import User
from app.schemas.like import LikeResponse

router = APIRouter(prefix="/api/v1/likes", tags=["likes"])


@router.post("")
def add_like(
    guide_id: int = Query(..., description="要点赞的攻略 ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """点赞攻略（需登录）。同一攻略只能点赞一次。"""
    existing = (
        db.query(Like)
        .filter(Like.user_id == current_user.id, Like.guide_id == guide_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="已经点赞过了")

    like = Like(user_id=current_user.id, guide_id=guide_id)
    db.add(like)
    db.commit()
    db.refresh(like)

    # 统计该攻略点赞数
    count = db.query(Like).filter(Like.guide_id == guide_id).count()

    return {
        "code": 201,
        "message": "点赞成功",
        "data": {**LikeResponse.model_validate(like).model_dump(), "like_count": count},
    }


@router.delete("/{guide_id}")
def remove_like(
    guide_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消点赞（需登录）。"""
    like = (
        db.query(Like)
        .filter(Like.user_id == current_user.id, Like.guide_id == guide_id)
        .first()
    )
    if not like:
        raise HTTPException(status_code=404, detail="尚未点赞该攻略")

    db.delete(like)
    db.commit()

    count = db.query(Like).filter(Like.guide_id == guide_id).count()

    return {
        "code": 200,
        "message": "已取消点赞",
        "data": {"like_count": count},
    }
