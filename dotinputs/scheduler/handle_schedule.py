import json
import logging
import requests
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.base import JobLookupError
from loader import bot
from ..buttons import get_habits_page
from telebot import types
from .core import scheduler
from config.environments import env


logging.basicConfig(level=logging.INFO)


def scheduled_message(chat_id, habit):
    mark = types.InlineKeyboardMarkup()
    complited = types.InlineKeyboardButton("Выполнить", callback_data=f"Выполнить:{habit}")
    passed = types.InlineKeyboardButton("Пропустить", callback_data=f"Пропустить:{habit}")
    mark.row(complited, passed)
    bot.send_message(chat_id, f'👇 👇 Вам необходимо выполнить привычку 👇 👇\n\n📌 "{habit}"', reply_markup=mark)


def set_cron(chat_id: int, habit: str, new_time: int) -> None:
    id_triger = str(chat_id) + habit
    scheduler.add_job(scheduled_message, IntervalTrigger(seconds=30), args=[chat_id, habit], id=id_triger)


def cancel_trigger(chat_id: int, habit: str) -> None:
    try:
        id_trigger = str(chat_id) + habit
        scheduler.remove_job(id_trigger)
    except JobLookupError:
        bot.send_message(chat_id, "Что то пошло не так")


def pause_trigger(chat_id, habits):
    for col in habits:
        id_trigger = str(chat_id) + col["name_habit"]
        scheduler.pause_job(id_trigger)


def resumes_trigger(chat_id, habits):
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
    text = call.data.split(":")
    mark = get_habits_page()
    if text[0] == "Выполнить":
        result = requests.patch(
            f"{env.MAIN_HOST}habit/status/{chat_id}/",
            json={"name_habit": text[1], "completed": True})
        if result.status_code == 202:
            data: dict = json.loads(result.text)
            if data["status"] == "Выполнено":
                cancel_trigger(chat_id, text[1])
                sms = f"❤️ Примите мои поздравления вы выполнили заданное количество повторений {text[1]}"
                bot.send_message(chat_id, sms, reply_markup=mark)
            else:
                sms = f'😊 Ваша привычка "{text[1]}" зафиксирована в БД.'
                bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        requests.patch(
            f"{env.MAIN_HOST}habit/status/{chat_id}/",
            json={"name_habit": text[1], "completed": False})
        sms = f'😌 Выполнение привычки "{text[1]}" перенесено на следующий раз'
        bot.send_message(chat_id, sms, reply_markup=mark)
    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
