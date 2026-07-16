from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse

router = APIRouter(tags=["comments"])


def _make_response(comment: Comment, author_name: str) -> dict:
    resp = CommentResponse.model_validate(comment)
    resp.author_name = author_name
    return resp.model_dump()


@router.get("/api/v1/guides/{guide_id}/comments")
def list_comments(
    guide_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="page_size"),
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
        u.id: u.username
        for u in db.query(User.id, User.username).filter(User.id.in_(author_ids)).all()
    }

    return {
        "code": 200,
        "message": "ok",
        "data": {
            "items": [_make_response(c, users_map.get(c.user_id, "")) for c in comments],
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
