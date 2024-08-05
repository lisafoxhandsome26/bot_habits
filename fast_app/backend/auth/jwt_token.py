import jwt
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from config.environments import env


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict) -> str:
    """Функция для создания токена"""
    encoded_jwt: str = jwt.encode(data, env.SECRET_KEY, algorithm=env.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Функция для декодирования токена"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, env.SECRET_KEY, algorithms=[env.ALGORITHM])
        chat: str = payload.get("sub")
        id_user: str = payload.get("user_id")
        if chat is None:
            raise credentials_exception
        return {"chat_id": int(chat), "user_id": int(id_user)}
    except InvalidTokenError:
        raise credentials_exception
