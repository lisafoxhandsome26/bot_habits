import logging
import requests
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from loader import bot
from ..buttons import get_habits_page
from telebot import types
from .core import scheduler
from config.environments import env
from ..database import dao


logging.basicConfig(level=logging.INFO)


def scheduled_message(chat_id, habit):
    """Функция для отправки сообщения об выполнении привычки"""
    mark = types.InlineKeyboardMarkup()
    complited = types.InlineKeyboardButton("Выполнить", callback_data=f"Выполнить:{habit}")
    passed = types.InlineKeyboardButton("Пропустить", callback_data=f"Пропустить:{habit}")
    mark.row(complited, passed)
    bot.send_message(chat_id, f'👇 👇 Вам необходимо выполнить привычку 👇 👇\n\n📌 "{habit}"', reply_markup=mark)


def set_cron(chat_id: int, habit: str, new_time: int) -> None:
    """Функция для установки автоматической отправки сообщения"""
    id_triger = str(chat_id) + habit
    scheduler.add_job(scheduled_message, IntervalTrigger(seconds=new_time), args=[chat_id, habit], id=id_triger)


def cancel_trigger(chat_id: int, habit: str) -> None:
    """Функция для отмены автоматической отправки сообщений"""
    try:
        id_trigger = str(chat_id) + habit
        scheduler.remove_job(id_trigger)
    except JobLookupError:
        bot.send_message(chat_id, "Что то пошло не так")


def pause_trigger(chat_id, habits):
    """Функция для временной остановки автоматических сообщений пользователя"""
    for col in habits:
        id_trigger = str(chat_id) + col["name_habit"]
        scheduler.pause_job(id_trigger)


def resumes_trigger(chat_id, habits):
    """Функция для возобновления отправки автомтических сообщений пользователю"""
    for col in habits:
        id_trigger = str(chat_id) + col["name_habit"]
        scheduler.resume_job(id_trigger)


@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("Выполнить") or
    call.data.startswith("Пропустить")
)
def record_execution(call):
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    trigger, name_habit = call.data.split(":")
    mark = get_habits_page()
    hashed = dao.get_hashed_data(chat_id)
    if trigger == "Выполнить":
        result = requests.patch(
            url=f"{env.MAIN_HOST}habit/status/",
            json={"name_habit": name_habit, "completed": True},
            headers={'Authorization': f'Bearer {hashed.jwt_token}'}
        )
        if result.status_code == 202:
            data: dict = result.json()
            if data["status"] == "Выполнено":
                cancel_trigger(chat_id, name_habit)
                sms = f"❤️ Примите мои поздравления вы выполнили заданное количество повторений {name_habit}"
                bot.send_message(chat_id, sms, reply_markup=mark)
            else:
                sms = f'😊 Ваша привычка "{name_habit}" зафиксирована в БД.'
                bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        requests.patch(
            url=f"{env.MAIN_HOST}habit/status/",
            json={"name_habit": name_habit, "completed": False},
            headers={'Authorization': f'Bearer {hashed.jwt_token}'}
        )
        sms = f'😌 Выполнение привычки "{name_habit}" перенесено на следующий раз'
        bot.send_message(chat_id, sms, reply_markup=mark)
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
