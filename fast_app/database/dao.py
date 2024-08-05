from datetime import datetime
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from config.async_database import db
from .models import User, Habit, Tracking


async def get_all_data_user(user_id: int) -> User | None:
    """Функция для получения данных  о пользователе"""
    stm = select(User).options(
        selectinload(User.habits)).filter_by(
        id=user_id,
    )
    async with db.session() as sos:
        result = await sos.execute(stm)
        return result.scalar()


async def add_user(user_data: dict) -> int:
    """Функция для добавления пользователя"""
    user = User(
        fullname=user_data["fullname"],
        age=user_data["age"],
        location=user_data["location"],
        purpose=user_data["purpose"],
        why=user_data["why"],
        hobby=user_data["hobby"],
        chat_id=user_data["chat_id"],
    )
    async with db.session() as sos:
        sos.add(user)
        await sos.commit()
        return user.id


async def get_list_habit(id_user: int) -> None:
    """Функция для получения списка привычек"""
    stm = select(Habit).filter_by(user_id=id_user)
    async with db.session() as sos:
        result = await sos.execute(stm)
        return result.scalars().all()


async def delete_habit(id_user: int, name_habit: str) -> None:
    """Функция для удаления привычки"""
    stm = delete(Habit).filter_by(name_habit=name_habit, user_id=id_user)
    async with db.session() as sos:
        await sos.execute(stm)
        await sos.commit()


async def edit_habit(id_user: int, old_name_habit: str, edit_data: dict) -> None:
    """Функция для изменения привычки"""
    stm = update(Habit).values(
        name_habit=edit_data["name_habit"],
        period=edit_data["period"],
        count_period=edit_data["count_period"],
    ).filter_by(user_id=id_user, name_habit=old_name_habit)
    async with db.session() as sos:
        await sos.execute(stm)
        await sos.commit()


async def edit_status(habit: Habit, completed: bool) -> None:
    """Функция для изменения статуса привычки"""
    async with db.session() as sos:
        if completed:
            habit.count_period -= 1
            habit.tracking.completed += 1
        else:
            habit.tracking.deferred += 1
        habit.tracking.last_update = datetime.now()
        sos.add(habit)
        await sos.commit()


async def add_habit(id_user: int, data_habit: dict) -> None:
    """Функция для добавления привычки"""
    habit = Habit(
        name_habit=data_habit["name_habit"],
        period=data_habit["period"],
        count_period=data_habit["count_period"],
        user_id=id_user,
    )
    async with db.session() as sos:
        sos.add(habit)
        await sos.commit()
        tracking = Tracking(habit_id=habit.id, completed=0, deferred=0)
        sos.add(tracking)
        await sos.commit()


async def get_habit(id_user: int, habit_name: str) -> Habit | None:
    """функция для получения привычки"""
    stm = select(Habit).filter_by(user_id=id_user, name_habit=habit_name)
    async with db.session() as sos:
        habit = await sos.execute(stm)
        return habit.scalars().one_or_none()
