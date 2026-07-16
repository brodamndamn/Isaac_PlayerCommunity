from datetime import datetime

from pydantic import BaseModel


class FavoriteResponse(BaseModel):
    """收藏记录响应"""

    id: int
    user_id: int
    guide_id: int
    guide_title: str = ""
    guide_author: str = ""
    guide_author_avatar: str | None = None
    guide_category: str = ""
    guide_cover: str | None = None
    guide_like_count: int = 0
    guide_fav_count: int = 0
    guide_is_liked: bool = False
    guide_is_favorited: bool = True  # 收藏列表中的必然是已收藏
    created_at: datetime

    model_config = {"from_attributes": True}


class FavoriteListData(BaseModel):
    items: list[FavoriteResponse]
    total: int
    page: int
    page_size: int
