import requests
from telebot import types
from loader import bot
from dotinputs.buttons import get_habits_page, get_authorization_buttons
from dotinputs.states import STATES, user_state
from config.environments import env
from .handle_registration import handle_question
from .utils import get_profile, get_data_user, check_authorization


@bot.message_handler(commands=["start"])
def start(message):
    """Основной обработчик"""
    id_chat: int = message.chat.id
    user_name: str = message.from_user.first_name
    user: dict = check_authorization(id_chat)
    if user != "Авторизоваться" and user is not False:
        sms, mark = get_data_user(user)
        bot.send_message(id_chat, sms, reply_markup=mark)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(id_chat, sms, reply_markup=mark)
    else:
        user_state[message.chat.id] = STATES['introduction']
        sms = (f"Привет {user_name}! Давай познакомимся 👱‍♂️.\n"
               f"Я бот полезных привычек, \n"
               f"я буду твоим помошником по улучшению твоей жизни.\n"
               f"Если ты согласен введи слово 'Да'.")
        mark = types.ReplyKeyboardRemove()
        bot.send_message(id_chat, sms, reply_markup=mark)
        bot.register_next_step_handler(message, on_click)


def on_click(message):
    id_chat: int = message.chat.id
    user_sms: str = message.text
    sms = ("Я очень рад что ты согласен менять свою жизнь 👱‍♂️.\n"
           "Для начала давай познакомимся поближе и зарегестрируемся.\n"
           "Для этого необходимо ответить на несколько вопросов.\n"
           "Если ты готов нажми слово 'Да' ✋.")
    if user_sms.lower().strip() == "да":
        bot.send_message(id_chat, sms)
        bot.register_next_step_handler(message, end_check)
    else:
        sms = ("Мне очень жаль что ты не готов менять свою жизнь.\n"
               "Если надумаешь дай мне знать я всегда рядом 🙁.")
        bot.send_message(id_chat, sms)
        bot.register_next_step_handler(message, start)


def end_check(message):
    id_chat: int = message.chat.id
    user_sms: str = message.text

    if user_sms.lower().strip() == "да":
        user_state[message.chat.id] = STATES['fullname']
        bot.send_message(id_chat, f"Какое твое полное имя?")
        handle_question(message)
    else:
        sms = "👱‍ Если вы надумаете дайте мне знать, я всегда рядом! /start"
        bot.send_message(id_chat, sms)
        bot.register_next_step_handler(message, start)


@bot.message_handler(func=lambda message: message.text == "Авторизоваться")
def authorization_user(message):
    """Обработчик профиля пользователя"""
    chat_id: int = message.chat.id
    requests.patch(
        f"{env.MAIN_HOST}profile_user/authenticated/{chat_id}/",
        json={"status": True}
    )
    sms, mark = get_profile(chat_id)
    bot.send_message(chat_id, sms, reply_markup=mark)


@bot.message_handler(func=lambda message: message.text == "Вкладка с привычками")
def page_habits(message):
    chat_id: int = message.chat.id
    user: dict = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        sms, mark = "Переходим на вкладку с привычками", get_habits_page()
        bot.send_message(chat_id, sms, reply_markup=mark)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        sms, mark = "Что то пошло не так", types.ReplyKeyboardRemove()
        bot.send_message(chat_id, sms, reply_markup=mark)


@bot.message_handler(func=lambda message: message.text == "Выйти из своего профиля")
def exit_profile(message):
    chat_id: int = message.chat.id
    requests.patch(
        f"{env.MAIN_HOST}profile_user/authenticated/{chat_id}/",
        json={"status": False}
    )
    mark = types.ReplyKeyboardRemove()
    bot.send_message(
        chat_id,
        "Выходим из профиля, чтобы заного войти в профиль можете нажать /start",
        reply_markup=mark
    )


@bot.message_handler(
    func=lambda message:
    message.text == "Вернуться назад" or
    message.text == "Узнать инфо о себе"
)
def comeback_or_info(message):
    chat_id: int = message.chat.id
    sms, mark = get_profile(chat_id)
    bot.send_message(chat_id, sms, reply_markup=mark)
