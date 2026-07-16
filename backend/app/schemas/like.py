from datetime import datetime

from pydantic import BaseModel


class LikeResponse(BaseModel):
    """点赞记录响应"""

    id: int
    user_id: int
    guide_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
