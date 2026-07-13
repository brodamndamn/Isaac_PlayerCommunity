from pydantic import BaseModel


class CharacterResponse(BaseModel):
    id: int
    name_en: str
    name_cn: str
    is_tainted: bool
    base_character_id: int | None
    health: str
    damage: float | None
    speed: float | None
    tears: float | None
    starting_items: list | None
    unlock_method: str | None
    description: str | None
    suitable_items: list | None
    image_url: str | None

    model_config = {"from_attributes": True}


class CharacterListData(BaseModel):
    items: list[CharacterResponse]
    total: int
    page: int
    page_size: int
