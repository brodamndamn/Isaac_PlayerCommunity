from datetime import datetime

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    """收藏记录响应"""

    id: int
    user_id: int
    guide_id: int
    guide_title: str = ""
    guide_author: str = ""
    guide_category: str = ""
    guide_cover: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteListData(BaseModel):
    items: list[FavoriteResponse]
    total: int
    page: int
    page_size: int
