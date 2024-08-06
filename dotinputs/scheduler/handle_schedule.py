import logging
import requests
from telebot import types
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from loader import bot
from ..buttons import get_habits_page
from .core import scheduler
from config.environments import env
from ..database import dao


main_habit = "Выгуливать пса"
logging.basicConfig(level=logging.INFO)


def scheduled_message(chat_id: int, habit: str) -> None:
    """Функция для отправки сообщения об выполнении привычки"""
    global main_habit
    main_habit = habit
    mark = types.InlineKeyboardMarkup()
    complited = types.InlineKeyboardButton("Выполнить", callback_data=f"Выполнить")
    passed = types.InlineKeyboardButton("Пропустить", callback_data=f"Пропустить")
    mark.row(complited, passed)
    bot.send_message(chat_id, f'👇 👇 Вам необходимо выполнить привычку 👇 👇\n\n📌 "{habit}"', reply_markup=mark)


def set_cron(chat_id: int, habit: str, new_time: int) -> None:
    """Функция для установки автоматической отправки сообщения"""
    id_trigger = str(chat_id) + habit
    scheduler.add_job(scheduled_message, IntervalTrigger(seconds=new_time), args=[chat_id, habit], id=id_trigger)


def cancel_trigger(chat_id: int, habit: str) -> None:
    """Функция для отмены автоматической отправки сообщений"""
    try:
        id_trigger = str(chat_id) + habit
        scheduler.remove_job(id_trigger)
    except JobLookupError:
        bot.send_message(chat_id, "Что то пошло не так")


def pause_trigger(chat_id: int, habits: list) -> None:
    """Функция для временной остановки автоматических сообщений пользователя"""
    for col in habits:
        id_trigger = str(chat_id) + col["name_habit"]
        scheduler.pause_job(id_trigger)


def resumes_trigger(chat_id: int, habits: list) -> None:
    """Функция для возобновления отправки автомтических сообщений пользователю"""
    for col in habits:
        id_trigger = str(chat_id) + col["name_habit"]
        scheduler.resume_job(id_trigger)


@bot.callback_query_handler(
    func=lambda call:
    call.data == "Выполнить" or
    call.data == "Пропустить"
)
def record_execution(call):
    global main_habit
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    trigger = call.data
    mark = get_habits_page()
    hashed = dao.get_hashed_data(chat_id)
    if trigger == "Выполнить":
        result = requests.patch(
            url=f"{env.MAIN_HOST}habit/status/",
            json={"name_habit": main_habit, "completed": True},
            headers={'Authorization': f'Bearer {hashed.jwt_token}'}
        )
        if result.status_code == 202:
            data: dict = result.json()
            if data["status"] == "Выполнено":
                cancel_trigger(chat_id, main_habit)
                sms = f"❤️ Примите мои поздравления по привычке - {main_habit} вы достигли лимита по выполнению."
                bot.send_message(chat_id, sms, reply_markup=mark)
            else:
                sms = f'😊 Ваша привычка "{main_habit}" зафиксирована в БД.'
                bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        requests.patch(
            url=f"{env.MAIN_HOST}habit/status/",
            json={"name_habit": main_habit, "completed": False},
            headers={'Authorization': f'Bearer {hashed.jwt_token}'}
        )
        sms = f'😌 Выполнение привычки "{main_habit}" перенесено на следующий раз'
        bot.send_message(chat_id, sms, reply_markup=mark)
    main_habit = "Выгуливать пса"
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
