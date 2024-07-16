import json
from datetime import datetime
import requests
from dotinputs import buttons as bn
from config.environments import env


def check_authorization(chat_id: int):
    """Функция для проверки авторизации пользователя"""
    result = requests.get(f"{env.MAIN_HOST}profile_user/{chat_id}/")
    if result.status_code == 200:
        user: dict = json.loads(result.text)["user"]
        if user['authorization']:
            return user
        return "Авторизоваться"
    return False


def get_profile(chat_id: int):
    """Функция для получения профиля пользователя"""
    user: dict = check_authorization(chat_id)
    if user:
        sms, mark = get_data_user(user)
        return sms, mark
    else:
        sms, mark = bn.get_authorization_buttons()
        return sms, mark


def get_data_user(user: dict):
    """Функция для создания и отправки информативного сообщения о пользователе"""
    try:
        sms = (f"👇👇 Ваш профиль пожалуйста 👇👇\n\n"
               f"📌 Ваше имя: {user['fullname']}\n"
               f"📌 Ваш текущий возраст: {user['age']}\n"
               f"📌 Место жительства: {user['location']}\n"
               f"📌 Ваша цель: {user['purpose']}\n"
               f"📌 Почему вы здесь: {user['why']}\n"
               f"📌 Ваше хобби: {user['hobby']}")
        mark = bn.get_profile_buttons()
        return sms, mark
    except TypeError:
        sms, mark = bn.get_authorization_buttons()
        return sms, mark


def get_sms_habits(habits: list[dict]):
    """Функция для создания и отправки информативного сообщения о привычках"""
    sms: str = "👇👇 Ваш список привычек 👇👇\n\n"
    mark = bn.get_habits_page()
    for col in habits:
        count = col.get("tracking").get("completed")
        deferred = col.get("tracking").get("deferred")
        last_update = col.get("tracking").get("last_update")

        if count:
            motivation = f"Вы молодцы 👍👍👍 Количество выполнений {count}."
        else:
            motivation = "🔥 Эта привычка еще ни разу не выполнялась."
        if deferred:
            deferr = f"Обратите на это внимание! Количество пропусков - {deferred}"
        else:
            deferr = f"🔥 Вы молодци эта привычка еще ни разу не откладывалась."

        day = round(col['period'] / 86400, 1)

        sms += (f"📌 {col['name_habit']}\n"
                f"Период уведомления каждые {day} дня.\n"
                f"Количество смс для отправки {col['count_period']}\n"
                f"Дата создания {col['created_at'][:16]}\n"
                f"Последнее обновление {last_update}\n"
                f"{deferr}\n"
                f"{motivation}\n\n")
    return sms, mark


def get_sms_for(habits: list[dict]):
    """Функция для получения списка привычек для удаления или изменения"""
    data_habits: dict = {}
    sms: str = "👇👇 Ваш список привычек 👇👇\n\n"
    for i, habit in enumerate(habits):
        sms += f'📌 {i+1} - {habit["name_habit"]}\n'
        data_habits[i+1] = habit
    return sms, data_habits


def validator_period(datetime_user: str):
    """Функция для проверки коректности вводимой даты для задания периода отправки смс"""
    datetime_user_obj = datetime.strptime(datetime_user, "%Y-%m-%d %H:%M:%S").timestamp()
    datetime_now_obj = datetime.now().timestamp()
    user_time, now_time = int(datetime_user_obj), int(datetime_now_obj)
    result_period = user_time - now_time
    if result_period < 86400:
        raise ValueError
    return result_period


def validator_params(param, chat_id):
    """Функция для проверки вводимых пользователем параметров"""
    period = param.get("period")
    count_period = param.get("count_period")
    name_habit = param.get("name_habit")
    if period:
        return validator_period(period)
    elif count_period:
        new_count = int(count_period)
        if new_count < 21:
            raise ValueError
        return new_count
    else:
        result = requests.get(f"{env.MAIN_HOST}/habit/{name_habit}/{chat_id}/")
        if result.status_code == 200:
            return name_habit
        else:
            raise ValueError
