from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from database import dao
from shemases import UserSchema, HabitSchema
from .auth.jwt_token import decode_access_token, oauth2_scheme

router = APIRouter()


"""Маршруты для взаимодействия с пользователями"""


@router.get("/profile_user/")
async def get_profile(token: str = Depends(oauth2_scheme)):
    """Получение данных о пользователе"""
    data: dict = decode_access_token(token)
    data_user = await dao.get_all_data_user(user_id=data.get("user_id"))
    if data_user:
        data: dict = UserSchema.model_validate(data_user, from_attributes=True).dict()
        return JSONResponse(status_code=200, content={"user": data})
    return JSONResponse(status_code=404, content={"result": False})


"""Маршруты для взаимодействия с привычками"""


@router.get("/list_habit/")
async def get_habits(token: str = Depends(oauth2_scheme)):
    """Получение списка привычек"""
    data: dict = decode_access_token(token)
    habits: list | None = await dao.get_list_habit(data.get("user_id"))
    if habits:
        data: list[dict] = [
            HabitSchema.model_validate(obj, from_attributes=True).dict()
            for obj in habits
        ]
        return JSONResponse(status_code=200, content={"result": True, "habits": data})
    return JSONResponse(status_code=404, content={"result": False, "habits": None})


@router.get("/habit/")
async def get_habit(habit_name=Body(), token: str = Depends(oauth2_scheme)):
    """Получение привычки"""
    name: str = habit_name.get("habit_name")
    data: dict = decode_access_token(token)
    result = await dao.get_habit(data.get("user_id"), name)
    if result is None:
        return JSONResponse(status_code=200, content={"result": True})
    return JSONResponse(status_code=404, content={"result": False})


@router.post("/habit/")
async def add_habits(habit_data=Body(), token: str = Depends(oauth2_scheme)):
    """Добавление привычки"""
    data_habits: dict = habit_data.get("data_habit")
    data: dict = decode_access_token(token)
    await dao.add_habit(data.get("user_id"), data_habits)
    return JSONResponse(status_code=201, content={"result": True})


@router.delete("/habit/")
async def delete_habits(name_habit=Body(), token: str = Depends(oauth2_scheme)):
    """Удаление привычки"""
    data: dict = decode_access_token(token)
    await dao.delete_habit(data.get("user_id"), name_habit.get("name_habit"))
    return JSONResponse(status_code=202, content={"result": True})


@router.patch("/habit/")
async def edit_habits(data_habits=Body(), token: str = Depends(oauth2_scheme)):
    """Редактирование привычки"""
    data: dict = decode_access_token(token)
    old_name_habit: str = data_habits.get("old_name_habit")
    edit_data: dict = data_habits.get("edit_data")
    await dao.edit_habit(data.get("user_id"), old_name_habit, edit_data)
    return JSONResponse(status_code=202, content={"result": True, "new_habit": edit_data, "old_name": old_name_habit})


@router.patch("/habit/status/")
async def edit_status_habit(data_habit=Body(), token: str = Depends(oauth2_scheme)):
    """Редактирование статуса привычки"""
    data: dict = decode_access_token(token)
    name_habit: str = data_habit.get("name_habit")
    completed: bool = data_habit.get("completed")
    habit = await dao.get_habit(data.get("user_id"), name_habit)
    if habit:
        if habit.count_period == 0:
            return JSONResponse(status_code=202, content={"status": "Выполнено"})
        else:
            await dao.edit_status(habit, completed)
            return JSONResponse(status_code=202, content={"status": "Изменено"})
    return JSONResponse(status_code=404, content={"status": "Not Found"})
