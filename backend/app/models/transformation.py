"""套装效果数据模型"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Transformation(Base):
    __tablename__ = "transformations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_cn: Mapped[str] = mapped_column(String(100), nullable=False)
    items_needed: Mapped[int] = mapped_column(Integer, nullable=False, comment="需要几个道具触发")
    required_items: Mapped[list] = mapped_column(JSON, nullable=False, comment="所需道具列表")
    effect: Mapped[str | None] = mapped_column(Text, nullable=True, comment="套装效果描述")
    item_pools: Mapped[list | None] = mapped_column(JSON, nullable=True, comment="道具池")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
