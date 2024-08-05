from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

from database.dao import add_user
from .hashing import get_password_hash, authenticate_user
from .jwt_token import create_access_token

auth_router = APIRouter()


@auth_router.post("/register/")
async def register(data=Body()):
    """Регистрация и добавление пользователя"""
    res: dict = data.get("data")
    chat_id: int = data.get("chat")
    if res:
        user_id: int = await add_user(res)
        access_token: str = create_access_token(
            data={"sub": str(chat_id), "user_id": str(user_id)}
        )
        h_pas: str = get_password_hash(str(chat_id))
        return JSONResponse(
            status_code=201,
            content={"token": access_token, "password": h_pas, "user_id": user_id})
    raise HTTPException(status_code=404, detail="Data are not found")


@auth_router.patch("/login/")
async def login(data=Body()):
    """Аутентификация пользователя"""
    credential_ext = HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    chat_id: int = data.get("chat_id")
    hashed_pass: str = data.get("hash_pass")
    user_id: int = data.get("user_id") # Сделать запрос к БД
    if not hashed_pass:
        raise credential_ext
    user: dict = authenticate_user(chat_id, hashed_pass)
    if not user:
        raise credential_ext
    access_token: str = create_access_token(
        data={"sub": str(chat_id), "user_id": str(user_id)}
    )
    return JSONResponse(status_code=200, content={"token": access_token})


@auth_router.patch("/logaut/")
async def logout(chat=Body()):
    """Разлогинивание пользователя"""
    chat_id: int = chat.get("chat")
    hash_jwt: str = get_password_hash(str(chat_id))
    return JSONResponse(status_code=202, content={"token": hash_jwt})
