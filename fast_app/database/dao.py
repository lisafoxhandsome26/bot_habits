from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from .core import session, engine
from .models import Base, User, Habit, Tracking


async def prepare_database() -> None:
    """Функция для подготовки базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    user = User(
        fullname="Александр Сергеев",
        age=27,
        location="смт Луганское",
        purpose="Улучшить свою жизнь",
        why="Хочу быть счастливым",
        hobby="Увлекаюсь компьютерами, машинами, и девушками",
        chat_id=921946846,
        authorization=True,
    )
    async with session() as sos:
        sos.add(user)
        await sos.commit()


async def check_user(message_id: int) -> int | None:
    """Функция для проверки пользователя"""
    stm = select(User.id).filter_by(chat_id=int(message_id), authorization=True)
    async with session() as sos:
        result = await sos.execute(stm)
        user_id = result.scalars().one_or_none()
        if user_id:
            return user_id


async def get_all_data_user(message_id: int) -> list | None:
    """Функция для получения данных  о пользователе"""
    stm = select(User).options(
        selectinload(User.habits)).filter_by(
        chat_id=message_id,
    )
    async with session() as sos:
        result = await sos.execute(stm)
        return result.scalars().one_or_none()


async def add_user(user_data: dict) -> None:
    """Функция для добавления пользователя"""
    user = User(
        fullname=user_data["fullname"],
        age=user_data["age"],
        location=user_data["location"],
        purpose=user_data["purpose"],
        why=user_data["why"],
        hobby=user_data["hobby"],
        chat_id=user_data["chat_id"],
        authorization=user_data["authorization"]
    )

    async with session() as sos:
        sos.add(user)
        await sos.commit()


async def get_list_habit(message_id: int) -> None:
    """Функция для получения списка привычек"""
    async with session() as sos:
        user_id: int = await check_user(message_id)
        if user_id:
            stm = select(Habit).filter_by(user_id=user_id)
            result = await sos.execute(stm)
            return result.scalars().all()


async def delete_habit(message_id: int, name_habit: str) -> None:
    """Функция для удаления привычки"""
    async with session() as sos:
        user_id: int = await check_user(message_id)
        if user_id:
            stm = delete(Habit).filter_by(name_habit=name_habit, user_id=user_id)
            await sos.execute(stm)
            await sos.commit()


async def edit_habit(message_id: int, old_name_habit: str, edit_data: dict) -> None:
    """Функция для изменения привычки"""
    async with session() as sos:
        user_id: int = await check_user(message_id)
        if user_id:
            stm = update(Habit).values(
                name_habit=edit_data["name_habit"],
                period=edit_data["period"],
                count_period=edit_data["count_period"],
            ).filter_by(user_id=user_id, name_habit=old_name_habit)
            await sos.execute(stm)
            await sos.commit()


async def authenticated(message_id: int, status: bool) -> None:
    """Функция для авторизации или выхода из профиля пользователя"""
    stm = update(User).values(authorization=status).filter_by(chat_id=message_id)
    async with session() as sos:
        await sos.execute(stm)
        await sos.commit()


async def add_habit(message_id: int, data_habit: dict) -> None:
    """Функция для добавления привычки"""
    async with session() as sos:
        user_id: int = await check_user(message_id)
        if user_id:
            habit = Habit(
                name_habit=data_habit["name_habit"],
                period=data_habit["period"],
                count_period=data_habit["count_period"],
                user_id=user_id,
            )
            sos.add(habit)
            await sos.commit()
            tracking = Tracking(habit_id=habit.id)
            sos.add(tracking)
            await sos.commit()
