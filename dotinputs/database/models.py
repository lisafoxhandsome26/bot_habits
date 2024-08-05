from sqlalchemy.orm import Mapped, mapped_column
from config.environments import Base


class HashedData(Base):
    __tablename__ = "hashed_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    password: Mapped[str]
    jwt_token: Mapped[str]
    chat_id: Mapped[int]
    user_id: Mapped[int]
