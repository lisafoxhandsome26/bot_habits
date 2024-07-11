from pydantic import BaseModel, field_serializer
from datetime import datetime


class UserSchema(BaseModel):
    fullname: str
    age: int
    location: str
    purpose: str
    why: str
    hobby: str
    authorization: bool
    habits: list["HabitSchema"] | None


class HabitSchema(BaseModel):
    name_habit: str
    period: int
    count_period: int
    created_at: datetime
    completed: int | None

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime):
        return str(created_at)
