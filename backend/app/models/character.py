from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(50), nullable=False)
    name_cn: Mapped[str] = mapped_column(String(50), nullable=False)
    is_tainted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="是否为里角色"
    )
    base_character_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("characters.id"), nullable=True, comment="里角色对应的表角色 ID"
    )
    health: Mapped[str] = mapped_column(String(50), nullable=False, comment="初始生命值")
    damage: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True, comment="初始攻击力"
    )
    speed: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True, comment="初始速度"
    )
    tears: Mapped[float | None] = mapped_column(
        Numeric(4, 2), nullable=True, comment="初始射速"
    )
    starting_items: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="初始携带道具 ID 数组"
    )
    unlock_method: Mapped[str | None] = mapped_column(Text, nullable=True, comment="解锁方式")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="角色特性描述")
    suitable_items: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="适合道具 ID 数组"
    )
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="图片路径")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
