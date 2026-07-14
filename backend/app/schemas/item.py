from datetime import datetime

from pydantic import BaseModel


class ItemResponse(BaseModel):
    """单个道具的 API 响应"""

    id: int
    name_en: str
    name_cn: str
    category: str
    quality: int | None
    description: str
    effect: str | None
    unlock_method: str | None
    pick_up_text: str | None
    recharge_time: str | None
    image_url: str | None
    item_pools: list | None
    stat_changes: list | None
    suitable_characters: list | None

    model_config = {"from_attributes": True}


class ItemListData(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "ok"
    data: ItemListData | None = None
