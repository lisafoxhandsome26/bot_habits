from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from database import dao
from shemases.shemases import UserSchema, HabitSchema


router = APIRouter()


"""Маршруты для взаимодействия с пользователями"""


@router.get("/profile_user/{message_id}/")
async def get_profile(message_id: int):
    """Получение данных о пользователе"""
    data_user = await dao.get_all_data_user(message_id=message_id)
    if data_user:
        data: dict = UserSchema.model_validate(data_user, from_attributes=True).dict()
        return JSONResponse(status_code=200, content={"user": data})
    return JSONResponse(status_code=404, content={"result": False})


@router.post("/profile_user/")
async def add_profile(data=Body()):
    """Добавление пользователя"""
    res = data.get("data")
    if res:
        await dao.add_user(res)
        return JSONResponse(status_code=201, content={"result": True})
    return JSONResponse(status_code=404, content={"result": False})


@router.patch("/profile_user/authenticated/{message_id}/")
async def authenticated_user(message_id: int, status=Body()):
    """Аутентификация пользователя"""
    res = status.get("status")
    await dao.authenticated(message_id, res)
    return JSONResponse(status_code=202, content={"result": True})


"""Маршруты для взаимодействия с привычками"""


@router.post("/habit/{message_id}/")
async def add_habits(message_id: int, habit_data=Body()):
    """Добавление привычки"""
    data = habit_data.get("data_habit")
    await dao.add_habit(message_id, data)
    return JSONResponse(status_code=201, content={"result": True})


@router.delete("/habit/{message_id}/")
async def delete_habits(message_id: int, name_habit=Body()):
    """Удаление привычки"""
    await dao.delete_habit(message_id, name_habit.get("name_habit"))
    return JSONResponse(status_code=202, content={"result": True})


@router.patch("/habit/{message_id}/")
async def edit_habits(message_id: int, data=Body()):
    """Редактирование привычки"""
    old_name_habit = data.get("old_name_habit")
    edit_data = data.get("edit_data")
    await dao.edit_habit(message_id, old_name_habit, edit_data)
    return JSONResponse(status_code=202, content={"result": True})


@router.get("/list_habit/{message_id}")
async def get_habits(message_id):
    """Получение списка привычек"""
    habits: list | None = await dao.get_list_habit(message_id)
    if habits:
        data: list[dict] = [
            HabitSchema.model_validate(obj, from_attributes=True).dict()
            for obj in habits
        ]
        return JSONResponse(status_code=200, content={"result": True, "habits": data})
    return JSONResponse(status_code=404, content={"result": False, "habits": None})
