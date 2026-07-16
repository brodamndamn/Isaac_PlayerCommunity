from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """发表评论请求体"""

    content: str = Field(min_length=1, max_length=2000, description="评论内容")


class CommentResponse(BaseModel):
    """评论响应"""

    id: int
    guide_id: int
    user_id: int
    author_name: str = ""
    author_avatar: str | None = None
    content: str
    like_count: int = 0
    is_liked: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
