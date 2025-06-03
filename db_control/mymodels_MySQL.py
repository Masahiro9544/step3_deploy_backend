from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass

class Words(Base):
    __tablename__ = 'words'
    id: Mapped[int] = mapped_column(primary_key=True)
    text_en: Mapped[str] = mapped_column()
    text_ja: Mapped[str] = mapped_column()
    translation: Mapped[str] = mapped_column()
    example: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    level: Mapped[str] = mapped_column()

class Progress(Base):
    __tablename__ = 'word_progress'
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))
    is_completed: Mapped[bool] = mapped_column()
    completed_date: Mapped[datetime | None] = mapped_column(nullable=True)

