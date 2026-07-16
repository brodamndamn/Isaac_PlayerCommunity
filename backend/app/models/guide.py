from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Guide(Base):
    __tablename__ = "guides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="正文（Markdown）")
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, comment="作者 ID"
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="item / character / ending / general"
    )
    related_item_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("items.id"), nullable=True, comment="关联道具"
    )
    related_character_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("characters.id"), nullable=True, comment="关联角色"
    )
    related_ending_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("endings.id"), nullable=True, comment="关联结局"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
