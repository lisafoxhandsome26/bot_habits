from typing import Annotated
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey


pk = Annotated[int, mapped_column(primary_key=True, index=True)]
date = Annotated[datetime, mapped_column(default=datetime.now)]
str_255 = Annotated[str, 255]
str_500 = Annotated[str, 500]


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[pk]
    fullname: Mapped[str_255]
    age: Mapped[int]
    location: Mapped[str_255]
    purpose: Mapped[str]
    why: Mapped[str]
    hobby: Mapped[str]
    chat_id: Mapped[int]
    authorization: Mapped[bool]
    habits: Mapped[list["Habit"] | None] = relationship()

    def __repr__(self):
        return f"User[{self.fullname}]"


class Habit(Base):
    __tablename__ = "habit"

    id: Mapped[pk]
    name_habit: Mapped[str_500]
    period: Mapped[int]
    count_period: Mapped[int]
    created_at: Mapped[date]
    tracking: Mapped["Tracking"] = relationship("Tracking", uselist=False, backref="habit", lazy="selectin")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"Habit[{self.name_habit}]"


class Tracking(Base):
    __tablename__ = "tracking"

    id: Mapped[pk]
    last_update: Mapped[date | None]
    completed: Mapped[int]
    deferred: Mapped[int]
    habit_id: Mapped["Habit"] = mapped_column(ForeignKey("habit.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"Tracking[{self.id}]"
