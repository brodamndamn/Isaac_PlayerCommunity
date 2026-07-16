from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from jose import JWTError, jwt

router = APIRouter(tags=["comments"])


def _make_response(comment: Comment, author_name: str) -> dict:
    resp = CommentResponse.model_validate(comment)
    resp.author_name = author_name
    return resp.model_dump()


def _get_opt_user(authorization: str | None, db: Session) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(authorization[7:], settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        uid = payload.get("sub")
        return db.query(User).filter(User.id == int(uid)).first() if uid else None
    except JWTError:
        return None


@router.get("/api/v1/guides/{guide_id}/comments")
def list_comments(
    guide_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """攻略评论列表（公开）。"""
    query = db.query(Comment).filter(Comment.guide_id == guide_id)

    total = query.count()
    comments = (
        query.order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 批量查询作者名
    author_ids = {c.user_id for c in comments}
    users_map = {
        u.id: (u.username, u.avatar)
        for u in db.query(User.id, User.username, User.avatar).filter(User.id.in_(author_ids)).all()
    }

    # 批量统计点赞数
    comment_ids = {c.id for c in comments}
    like_map: dict[int, int] = {}
    if comment_ids:
        for cid, cnt in db.query(CommentLike.comment_id, func.count()).filter(
            CommentLike.comment_id.in_(comment_ids)
        ).group_by(CommentLike.comment_id).all():
            like_map[cid] = cnt

    # 当前用户点赞状态
    liked_set: set[int] = set()
    cur = _get_opt_user(authorization, db)
    if cur and comment_ids:
        for (cid,) in db.query(CommentLike.comment_id).filter(
            CommentLike.user_id == cur.id, CommentLike.comment_id.in_(comment_ids)
        ).all():
            liked_set.add(cid)

    items = []
    for c in comments:
        resp = CommentResponse.model_validate(c)
        name, av = users_map.get(c.user_id, ("", None))
        resp.author_name = name
        resp.author_avatar = av
        resp.like_count = like_map.get(c.id, 0)
        resp.is_liked = c.id in liked_set
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


@router.post("/api/v1/guides/{guide_id}/comments")
def create_comment(
    guide_id: int,
    body: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发表评论（需登录）。"""
    comment = Comment(
        guide_id=guide_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "code": 201,
        "message": "评论成功",
        "data": _make_response(comment, current_user.username),
    }


@router.delete("/api/v1/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除评论（需登录，仅作者或 admin 可删）。"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if current_user.id != comment.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此评论")

    db.delete(comment)
    db.commit()

    return {
        "code": 200,
        "message": "删除成功",
        "data": None,
    }


@router.post("/api/v1/comments/{comment_id}/like")
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """点赞评论（需登录）。"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    existing = db.query(CommentLike).filter(
        CommentLike.user_id == current_user.id, CommentLike.comment_id == comment_id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="已经点赞过了")

    db.add(CommentLike(user_id=current_user.id, comment_id=comment_id))
    db.commit()
    count = db.query(func.count()).filter(CommentLike.comment_id == comment_id).scalar() or 0
    return {"code": 201, "message": "点赞成功", "data": {"like_count": count}}


@router.delete("/api/v1/comments/{comment_id}/like")
def unlike_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消评论点赞（需登录）。"""
    like = db.query(CommentLike).filter(
        CommentLike.user_id == current_user.id, CommentLike.comment_id == comment_id
    ).first()
    if not like:
        raise HTTPException(status_code=404, detail="尚未点赞")

    db.delete(like)
    db.commit()
    count = db.query(func.count()).filter(CommentLike.comment_id == comment_id).scalar() or 0
    return {"code": 200, "message": "已取消点赞", "data": {"like_count": count}}
