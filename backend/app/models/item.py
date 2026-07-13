from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_cn: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="active / passive / trinket / card / pill"
    )
    quality: Mapped[int | None] = mapped_column(TINYINT, nullable=True, comment="品质 0-4")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="功能描述")
    effect: Mapped[str | None] = mapped_column(Text, nullable=True, comment="具体效果机制")
    unlock_method: Mapped[str | None] = mapped_column(Text, nullable=True, comment="解锁方式")
    suitable_characters: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="适合角色 ID 数组"
    )
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="图片路径")
    pick_up_text: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="拾取文字"
    )
    recharge_time: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="充能时间（仅主动道具）"
    )
    item_pools: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, comment="道具池列表"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
