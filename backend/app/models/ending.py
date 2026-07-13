from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Ending(Base):
    __tablename__ = "endings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False, comment="英文名")
    name_cn: Mapped[str] = mapped_column(String(100), nullable=False, comment="中文名")
    ending_number: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="结局编号（游戏内编号 1-22+）"
    )
    completion_method: Mapped[str] = mapped_column(
        Text, nullable=False, comment="完成方式（如「击败 Mega Satan」）"
    )
    unlock_method: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="解锁该结局区域的条件"
    )
    required_character: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="是否强制某一角色（NULL 表示不强制）"
    )
    boss_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="最终 Boss 名称")
    unlocks: Mapped[list | None] = mapped_column(
        JSON, nullable=True, comment="完成后解锁的内容（角色/道具名称数组）"
    )
    image_url: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="结局画面图片路径"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
