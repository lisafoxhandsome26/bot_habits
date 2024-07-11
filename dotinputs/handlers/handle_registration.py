import requests
from requests import Response
from loader import bot
from dotinputs.states import user_state, STATES
from dotinputs.buttons import get_profile_buttons
from config.environments import env
from telebot import types


user_data: dict = {}


@bot.message_handler(func=lambda message: message.chat.id in user_state)
def handle_question(message):
    global user_data
    chat_id: int = message.chat.id
    state = user_state[chat_id]
    if state == STATES['fullname']:
        user_state[chat_id] = STATES['age']
    elif state == STATES['age']:
        bot.send_message(chat_id, f"Сколько тебе полных лет?")
        user_data["fullname"] = message.text
        user_state[chat_id] = STATES['location']
    elif state == STATES['location']:
        try:
            user_data["age"] = int(message.text)
            bot.send_message(chat_id, f"Где ты сейчас проживаешь?")
            user_state[chat_id] = STATES['purpose']
        except ValueError:
            bot.send_message(chat_id, f"😠 Ты ввел некоректное значение, введи число!")
    elif user_state[chat_id] == STATES['purpose']:
        bot.send_message(chat_id, "Какой цели ты бы хотел достигнуть?")
        user_data["location"] = message.text
        user_state[chat_id] = STATES['why']
    elif state == STATES['why']:
        bot.send_message(chat_id, "Почему ты хочешь поменять свой образ жизни?")
        user_data["purpose"] = message.text
        user_state[chat_id] = STATES['hobby']
    elif state == STATES['hobby']:
        bot.send_message(chat_id, "Какие твои интересы, хобби?")
        user_data["why"] = message.text
        user_state[chat_id] = STATES['register']
    elif state == STATES['register']:
        user_data["hobby"] = message.text
        user_data["chat_id"] = chat_id
        user_data["authorization"] = True
        sms = ("Спасибо за твои ответы! 👱‍♂️\n"
               "Теперь ты можешь устанавливать свои новые привычки,\n"
               "а я буду их контролировать.")

        result: Response = requests.post(f"{env.MAIN_HOST}profile_user/", json={"data": user_data})
        if result.status_code == 201:
            mark = get_profile_buttons()
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
        user_data = {}
        del user_state[chat_id]
