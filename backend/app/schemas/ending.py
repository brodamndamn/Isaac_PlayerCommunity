from pydantic import BaseModel


class EndingResponse(BaseModel):
    id: int
    name_en: str
    name_cn: str
    ending_number: int
    completion_method: str
    unlock_method: str | None
    required_character: str | None
    boss_name: str
    unlocks: list | None
    image_url: str | None

    model_config = {"from_attributes": True}


class EndingListData(BaseModel):
    items: list[EndingResponse]
    total: int
    page: int
    page_size: int
