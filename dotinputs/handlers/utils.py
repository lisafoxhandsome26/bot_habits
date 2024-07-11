from config.environments import env
from requests import Response
import requests
import json
from dotinputs import buttons as bn


def check_authorization(chat_id: int):
    result: Response = requests.get(f"{env.MAIN_HOST}profile_user/{chat_id}/")
    if result.status_code == 200:
        user: dict = json.loads(result.text)["user"]
        if user['authorization']:
            return user
        return "Авторизоваться"
    return False


def get_profile(chat_id: int):
    user: dict = check_authorization(chat_id)
    if user:
        sms, mark = get_data_user(user)
        return sms, mark
    else:
        sms, mark = bn.get_authorization_buttons()
        return sms, mark


def get_data_user(user: dict):
    try:
        sms = (f"👇👇👇 Ваш профиль пожалуйста 👇👇👇\n\n"
               f"Ваше имя: {user['fullname']}\n"
               f"Ваш текущий возраст: {user['age']}\n"
               f"Место жительства: {user['location']}\n"
               f"Ваша цель: {user['purpose']}\n"
               f"Почему вы здесь: {user['why']}\n"
               f"Ваше хобби: {user['hobby']}")
        mark = bn.get_profile_buttons()
        return sms, mark
    except TypeError:
        sms, mark = bn.get_authorization_buttons()
        return sms, mark


def get_sms_habits(habits: list[dict]):
    sms: str = "👇👇 Ваш список привычек и статус выполнения 👇👇\n\n"
    mark = bn.get_habits_page()
    for col in habits:
        count = col.get("completed")
        if count:
            motivation = f"Вы молодцы 👍👍👍 Количество выполнений {count}"
        else:
            motivation = "Эта привычка еще ни разу не выполнялась"

        sms += (f"📌 {col['name_habit']}\n"
                f"Промежуток времени {col['period']}\n"
                f"Количество выполнений {col['count_period']}\n"
                f"Дата начала {col['created_at'][:16]}\n"
                f"{motivation}\n\n")
    return sms, mark


def get_sms_for_delete(habits: list[dict]):
    data_del: dict = {}
    sms: str = "👇👇 Cписок привычек для удаления 👇👇\n\n"
    for i, name_habit in enumerate(habits):
        sms += f'📌 {i+1} - {name_habit["name_habit"]}\n'
        data_del[i+1] = name_habit["name_habit"]
    return sms, data_del


def get_sms_for_edit(habits: list[dict]):
    data_edit: dict = {}
    sms: str = "👇👇 Cписок привычек для изменеия 👇👇\n\n"
    for i, habit in enumerate(habits):
        sms += f'📌 {i+1} - {habit["name_habit"]}\n'
        data_edit[i+1] = habit
    return sms, data_edit
