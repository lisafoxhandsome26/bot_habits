from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    """Функция для верификации пользователя"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Функция для получения хешированого пароля"""
    return pwd_context.hash(password)


def authenticate_user(chat_id: int, hash_pass: str) -> dict | bool:
    """Аутентификация пользователя"""
    if not verify_password(str(chat_id), hash_pass):
        return False
    return {"chat_id": chat_id, "hash_pass": hash_pass}
