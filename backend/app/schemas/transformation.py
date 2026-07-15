"""套装效果 Pydantic 模型"""
from pydantic import BaseModel


class EnrichedItem(BaseModel):
    id: int | None = None
    name_en: str
    name_cn: str
    image_url: str | None


class TransformationResponse(BaseModel):
    id: int
    name_en: str
    name_cn: str
    items_needed: int
    required_items: list
    effect: str | None
    item_pools: list | None
    required_items_enriched: list[EnrichedItem] | None = None
    first_item_id: int | None = None

    model_config = {"from_attributes": True}


class TransformationListData(BaseModel):
    items: list[TransformationResponse]
    total: int
