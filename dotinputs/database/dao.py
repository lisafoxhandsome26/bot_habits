from sqlalchemy import select
from .models import HashedData
from config.sync_database import db


def get_hashed_data(chat_id: int) -> HashedData | None:
    """Функция для получения хешированого пароля и токена"""
    with db.sync_session() as sos:
        stm = select(HashedData).filter_by(chat_id=chat_id)
        res = sos.execute(stm)
        hashed_data = res.scalar()
        if hashed_data:
            return hashed_data
        return None


def add_hash_data(chat_id: int, hash_data: dict) -> None:
    """Функция для добавления хешированого пароля и токена"""
    hashed = HashedData(
        password=hash_data.get("password"),
        jwt_token=hash_data.get("token"),
        user_id=hash_data.get("user_id"),
        chat_id=chat_id
    )
    with db.sync_session() as sos:
        sos.add(hashed)
        sos.commit()


def authenticated(chat_id: int, updated_jwt: str) -> None:
    """Функция для авторизации или выхода из профиля пользователя"""
    stm = select(HashedData).filter_by(chat_id=chat_id)
    with db.sync_session() as sos:
        res = sos.execute(stm)
        hashed_data = res.scalar()
        hashed_data.jwt_token = updated_jwt
        sos.commit()
