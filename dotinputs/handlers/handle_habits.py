import json

import requests
from telebot import types
from .utils import check_authorization, get_sms_habits, get_sms_for_delete, get_sms_for_edit
from loader import bot
from dotinputs.buttons import get_habits_page, get_authorization_buttons, get_yes_or_no
from dotinputs.states import habit_state, STATES_ADD_HABIT, habit_data
from config.environments import env


habit_state_edit: dict = {}
habit_data_edit: dict = {"old_name_habit": None, "edit_data": None}
STATES_EDIT = {
    "name_habit": "name_habit",
    "period": "period",
    "count_period": "count_period",
    "end_edit": "end_edit"
}


"""Просмотр привычек"""


@bot.message_handler(func=lambda message: message.text == "Перейти на статус привычек")
def habits(message):
    chat_id: int = message.chat.id
    result = requests.get(f"{env.MAIN_HOST}list_habit/{chat_id}/")
    if result.status_code == 200:
        list_habits = json.loads(result.text)["habits"]
        sms, mark = get_sms_habits(list_habits)
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        result = check_authorization(chat_id)
        if result != "Авторизоваться" and result is not False:
            mark = get_habits_page()
            sms = "Ваш список привычек еще пуст"
            bot.send_message(chat_id, sms, reply_markup=mark)
        elif result == "Авторизоваться":
            sms, mark = get_authorization_buttons()
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


"""Добавление привычки"""


@bot.message_handler(func=lambda message: message.text == "Добавить привычку")
def add_habits(message):
    chat_id: int = message.chat.id
    user: dict = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        habit_state[message.chat.id] = STATES_ADD_HABIT['name_habit']
        mark = types.ReplyKeyboardRemove()
        bot.send_message(chat_id, "Введите название привычки", reply_markup=mark)
        bot.register_next_step_handler(message, add_habit)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


@bot.message_handler(func=lambda message: message.chat.id in habit_state)
def add_habit(message):
    global habit_data
    chat_id = message.chat.id
    state = habit_state[chat_id]
    if state == STATES_ADD_HABIT['name_habit']:
        bot.send_message(chat_id, f"Какой период задашь?")
        habit_data["name_habit"] = message.text
        habit_state[chat_id] = STATES_ADD_HABIT['period']
    elif state == STATES_ADD_HABIT['period']:
        try:
            habit_data["period"] = int(message.text)
            habit_state[chat_id] = STATES_ADD_HABIT['count_period']
            bot.send_message(chat_id, f"Сколько повторений задашь?")
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")
    elif state == STATES_ADD_HABIT['count_period']:
        try:
            habit_data["count_period"] = int(message.text)
            requests.post(
                f"{env.MAIN_HOST}habit/{chat_id}/",
                json={"data_habit": habit_data}
            )
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")
        habit_data = {}
        mark = get_habits_page()
        del habit_state[chat_id]
        bot.send_message(chat_id, f"Твоя привычка успешно добавлена", reply_markup=mark)


"""Удаление привычки"""


@bot.message_handler(func=lambda message: message.text == "Удалить привычку")
def remove_habits(message):
    chat_id: int = message.chat.id
    user: dict = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        result = requests.get(f"{env.MAIN_HOST}list_habit/{chat_id}/")
        if result.status_code == 200:
            list_habits = json.loads(result.text)["habits"]
            sms, data_del = get_sms_for_delete(list_habits)
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
            bot.send_message(chat_id, "Выберите номер привычки для удаления.")
            bot.register_next_step_handler(message, choice_del_habit, data_del, sms)
        else:
            sms = "Ваш спиок привычек пуст."
            mark = get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


def choice_del_habit(message, data_del, sms_for_del):
    chat_id = message.chat.id
    try:
        name_habit = data_del[int(message.text)]
        calling_yes = f"YES:{name_habit}"
        calling_no = f"NO:{name_habit}"
        mark = get_yes_or_no(calling_yes, calling_no)
        sms = f'Вы уверены что хотите удалить привычку - "{name_habit}"?'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        mark = types.ReplyKeyboardRemove()
        bot.reply_to(message, "Выберите пожалуйста коректный номер привычки!")
        bot.send_message(chat_id, sms_for_del, reply_markup=mark)
        bot.register_next_step_handler(message, choice_del_habit, data_del, sms_for_del)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("NO") or call.data.startswith("YES")
)
def make_delete_habit(call):
    chat_id: int = call.message.chat.id
    text: list = call.data.split(":")
    mark = get_habits_page()
    if text[0] == "NO":
        sms = f'Удаление привычки "{text[1]}" не выполненно.'
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        url = f"{env.MAIN_HOST}habit/{chat_id}/"
        result = requests.delete(url, json={"name_habit": text[1]})
        if result.status_code == 204:
            sms = f'Ваша привычка "{text[1]}" успешно удалена'
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)


"""Изменение привычки"""


@bot.message_handler(func=lambda message: message.text == "Изменить привычку")
def edit_habits(message):
    chat_id: int = message.chat.id
    user: dict = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        result = requests.get(f"{env.MAIN_HOST}list_habit/{chat_id}/")
        if result.status_code == 200:
            list_habits = json.loads(result.text)["habits"]
            sms, data_edit = get_sms_for_edit(list_habits)
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
            bot.send_message(chat_id, "Выберите номер привычки для изменения.")
            bot.register_next_step_handler(message, choice_edit_habit, data_edit, sms)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


def choice_edit_habit(message, data_edit, sms_for_edit):
    chat_id = message.chat.id
    try:
        global habit_data_edit
        habit = data_edit[int(message.text)]
        name_habit = habit['name_habit']
        habit_data_edit['edit_data'] = habit
        habit_data_edit["old_name_habit"] = name_habit

        mark = types.InlineKeyboardMarkup()
        name = types.InlineKeyboardButton(
            "Название",
            callback_data=f"name_habit:{name_habit}"
        )
        period = types.InlineKeyboardButton(
            "Период",
            callback_data=f"period:{name_habit}"
        )
        count_period = types.InlineKeyboardButton(
            "Количество повторений",
            callback_data=f"count_period:{name_habit}"
        )
        all_params = types.InlineKeyboardButton(
            "Все параметры",
            callback_data=f"all_params:{name_habit}"
        )
        mark.row(name, count_period)
        mark.row(period, all_params)
        sms = f'Вы выбрали для изменения привычку - "{name_habit}". Вебирите параметр'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        mark = types.ReplyKeyboardRemove()
        bot.reply_to(message, f"Выберите пожалуйста коректный номер привычки!")
        bot.send_message(chat_id, sms_for_edit, reply_markup=mark)
        bot.register_next_step_handler(message, choice_edit_habit, data_edit, sms_for_edit)


@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("name_habit") or
    call.data.startswith("period") or
    call.data.startswith("count_period") or
    call.data.startswith("all_params")
)
def callback_edit(callback):
    chat_id: int = callback.message.chat.id
    text: list = callback.data.split(":")
    if text[0] == "name_habit":
        bot.send_message(chat_id, "Введите новое название.")
        old_name = habit_data_edit["old_name_habit"]
        sms = f'Вы уверены что хотите изменить имя привычки с {old_name} на'
        bot.register_next_step_handler(callback.message, edit_param, text[1], sms)
    elif text[0] == "period":
        bot.send_message(chat_id, "Введите новое период.")
        old_period = habit_data_edit["edit_data"]['period']
        sms = f'Вы уверены что хотите изменить время отправки смс с {old_period} на'
        bot.register_next_step_handler(callback.message, edit_param, text[1], sms)
    elif text[0] == "count_period":
        bot.send_message(chat_id, "Введите новое частоту отправки смс.")
        old_count = habit_data_edit["edit_data"]['count_period']
        sms = f'Вы уверены что хотите изменить количество смс с {old_count} на'
        bot.register_next_step_handler(callback.message, edit_param, text[1], sms)
    else:
        habit_state_edit[chat_id] = STATES_EDIT['name_habit']
        sms = "Введите новое название привычки"
        bot.send_message(chat_id, sms)
        edit_all_params(callback.message)


@bot.message_handler(func=lambda message: message.chat.id in habit_state_edit)
def edit_all_params(message):
    global habit_data_edit
    chat_id: int = message.chat.id
    state = habit_state_edit[chat_id]
    if state == STATES_EDIT['name_habit']:
        habit_state_edit[chat_id] = STATES_EDIT['period']
    elif state == STATES_EDIT['period']:
        sms = "Введи новый период действия"
        bot.send_message(chat_id, sms)
        habit_data_edit['edit_data']['name_habit'] = message.text
        habit_state_edit[chat_id] = STATES_EDIT['count_period']
        bot.send_message(chat_id, f"Введите пожалуйста целое число!")
    elif state == STATES_EDIT['count_period']:
        try:
            sms = "Введи новую частоту отправки смс"
            bot.send_message(chat_id, sms)
            habit_data_edit['edit_data']['period'] = int(message.text)
            habit_state_edit[chat_id] = STATES_EDIT['end_edit']
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")
    elif state == STATES_EDIT['end_edit']:
        try:
            old_name = habit_data_edit["old_name_habit"]
            habit_data_edit['edit_data']['count_period'] = int(message.text)
            mark = get_yes_or_no(f"yes:{old_name}", f"no:{old_name}")
            sms = f'Вы уверены что хотите изменить привычку "{old_name}"?'
            bot.send_message(chat_id, sms, reply_markup=mark)
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")


def edit_param(message, key, sms):
    global habit_data_edit
    chat_id, new_param = message.chat.id, message.text
    old_name = habit_data_edit['old_name_habit']
    habit_data_edit["edit_data"][key] = new_param
    mark = get_yes_or_no(f"yes:{old_name}", f"no:{old_name}")
    sms += f" {new_param}?"
    bot.send_message(chat_id, sms, reply_markup=mark)


@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("no") or
    call.data.startswith("yes")
)
def make_edit_habit(call):
    global habit_data_edit, habit_state_edit
    chat_id: int = call.message.chat.id
    text: list = call.data.split(":")
    mark = get_habits_page()
    if text[0] == "yes":
        url = f"{env.MAIN_HOST}habit/{chat_id}/"
        result = requests.patch(url, json=habit_data_edit)
        if result.status_code == 204:
            sms = f"Ваша привычка {text[1]} успешно изменена"
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
        habit_data_edit = {"old_name_habit": None, "edit_data": None}
        habit_state_edit[chat_id] = None
    else:
        sms = f'Изменение привычки c "{text[1]}" не произошло'
        bot.send_message(chat_id, sms, reply_markup=mark)


"""Обработка неизвестных сообщений"""


@bot.message_handler()
def manage_habits(message):
    bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")

# Добавить по 5 привчек на вывод и с кнопкой для добавления следующих 5 и т.д.
# Есть такой баг когда пользователь только заходит и Вводит "Вернуться назад" он может попасть не на ту страницу
# Реализовать удаление привычки
# Реализовать редактирование привычки
# Пересмотреть структуру БД и типы данных в БД
# Запустить все в docker compose
# Просмотреть автооризацию через FastAPI токен если несложно переделать - ВНЕДРИТЬ!
