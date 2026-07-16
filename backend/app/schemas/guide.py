from datetime import datetime

from pydantic import BaseModel, Field


class GuideCreate(BaseModel):
    """创建攻略请求体"""

    title: str = Field(min_length=1, max_length=200, description="标题")
    content: str = Field(min_length=1, description="正文（Markdown）")
    category: str = Field(description="分类：item / character / ending / general")
    cover_image: str | None = None
    related_item_id: int | None = None
    related_character_id: int | None = None
    related_ending_id: int | None = None


class GuideResponse(BaseModel):
    """攻略响应"""

    id: int
    title: str
    content: str
    author_id: int
    author_name: str = ""
    author_avatar: str | None = None
    category: str
    cover_image: str | None = None
    related_item_id: int | None
    related_character_id: int | None
    related_ending_id: int | None
    like_count: int = 0
    favorite_count: int = 0
    comment_count: int = 0
    is_liked: bool = False
    is_favorited: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GuideListData(BaseModel):
    items: list[GuideResponse]
    total: int
    page: int
    page_size: int
