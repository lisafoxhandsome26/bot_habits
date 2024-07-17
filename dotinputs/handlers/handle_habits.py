import json
from datetime import datetime

import requests
from telebot import types

from .utils import check_authorization, get_sms_habits, get_sms_for, validator_params, validator_period
from loader import bot
from dotinputs.buttons import get_habits_page, get_authorization_buttons, get_yes_or_no
from dotinputs.scheduler.handle_schedule import set_cron, cancel_trigger
from config.environments import env

habit_data: dict = {}
habit_state_edit: dict = {}
habit_state: dict = {}

habit_data_edit: dict = {"old_name_habit": None, "edit_data": None}

STATES_ADD_HABIT: dict = {
    "name_habit": 'name_habit',
    'period': 'period',
    'count_period': 'count_period'
}

STATES_EDIT: dict = {
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


"""Удаление привычки"""


@bot.message_handler(func=lambda message: message.text == "Удалить привычку")
def remove_habits(message):
    chat_id: int = message.chat.id
    user = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        result = requests.get(f"{env.MAIN_HOST}list_habit/{chat_id}/")
        if result.status_code == 200:
            list_habits = json.loads(result.text)["habits"]
            sms, data_del = get_sms_for(list_habits)
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
        name_habit = data_del[int(message.text)]["name_habit"]
        calling_yes = f"YES:{name_habit}"
        calling_no = f"NO:{name_habit}"
        mark = get_yes_or_no(calling_yes, calling_no)
        sms = f'Вы уверены что хотите удалить привычку - "{name_habit}"?'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        mark = types.ReplyKeyboardRemove()
        sms = "Выберите пожалуйста коректный номер привычки!"
        bot.reply_to(message, sms)
        bot.send_message(chat_id, sms_for_del, reply_markup=mark)
        bot.register_next_step_handler(message, choice_del_habit, data_del, sms_for_del)


@bot.callback_query_handler(
    func=lambda call:
    call.data.startswith("NO") or
    call.data.startswith("YES")
)
def make_delete_habit(call):
    chat_id: int = call.message.chat.id
    trigger, name_habit = call.data.split(":")
    mark = get_habits_page()
    if trigger == "NO":
        sms = f'Удаление привычки "{name_habit}" не выполненно.'
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        url = f"{env.MAIN_HOST}habit/{chat_id}/"
        result = requests.delete(url, json={"name_habit": name_habit})

        if result.status_code == 202:
            cancel_trigger(chat_id, name_habit)
            sms = f'Ваша привычка "{name_habit}" успешно удалена'
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)


"""Добавление привычки"""


@bot.message_handler(func=lambda message: message.text == "Добавить привычку")
def add_habits(message):
    chat_id: int = message.chat.id
    user = check_authorization(chat_id)
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
        try:
            result = requests.get(f"{env.MAIN_HOST}/habit/{message.text}/{chat_id}/")
            if result.status_code == 200:
                habit_data["name_habit"] = message.text
                habit_state[chat_id] = STATES_ADD_HABIT['period']
                sms = f'Введите дату первого напоминания привычки в формате: {str(datetime.now())[:-7]}'
                bot.send_message(chat_id, sms)
            else:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста уникальное название привычки!")
    elif state == STATES_ADD_HABIT['period']:
        try:
            result_period: int = validator_period(message.text)
            sms = "Сколько раз отправлять уведомления? Введите число не менее 21"
            habit_data["period"] = result_period
            habit_state[chat_id] = STATES_ADD_HABIT['count_period']
            bot.send_message(chat_id, sms)
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста коректное значение!")
    elif state == STATES_ADD_HABIT['count_period']:
        try:
            number: int = int(message.text)
            if number < 21:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста коректное значение!")
        else:
            habit_data["count_period"] = number
            requests.post(
                f"{env.MAIN_HOST}habit/{chat_id}/",
                json={"data_habit": habit_data}
            )
            name_habit = habit_data["name_habit"]
            new_time = habit_data["period"]
            set_cron(chat_id, name_habit, new_time)

            habit_data = {}
            del habit_state[chat_id]

            sms, mark = "Твоя привычка успешно добавлена", get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)


"""Изменение привычки"""


@bot.message_handler(func=lambda message: message.text == "Изменить привычку")
def edit_habits(message):
    chat_id: int = message.chat.id
    user = check_authorization(chat_id)
    if user != "Авторизоваться" and user is not False:
        result = requests.get(f"{env.MAIN_HOST}list_habit/{chat_id}/")
        if result.status_code == 200:
            list_habits = json.loads(result.text)["habits"]
            sms, data_edit = get_sms_for(list_habits)
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
            bot.send_message(chat_id, "Выберите номер привычки для изменения.")
            bot.register_next_step_handler(message, choice_edit_habit, data_edit, sms)
        else:
            sms = "Ваш список привычек пуст."
            mark = get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)
    elif user == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


def choice_edit_habit(message, data_edit, sms_for_edit):
    chat_id: int = message.chat.id
    try:
        global habit_data_edit
        habit = data_edit[int(message.text)]
        name_habit = habit['name_habit']
        habit_data_edit['edit_data'] = habit
        habit_data_edit["old_name_habit"] = name_habit

        mark = types.InlineKeyboardMarkup()
        name = types.InlineKeyboardButton("Название", callback_data=f"name_habit:{name_habit}")
        period = types.InlineKeyboardButton("Период", callback_data=f"period:{name_habit}")
        count_period = types.InlineKeyboardButton("Количество смс", callback_data=f"count_period:{name_habit}")
        all_params = types.InlineKeyboardButton("Все параметры", callback_data=f"all_params:{name_habit}")
        mark.row(name, count_period)
        mark.row(period, all_params)

        sms = f'Вы выбрали для изменения привычку - "{name_habit}". Вебирите параметр'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        sms, mark = f"Выберите пожалуйста коректный номер привычки!", types.ReplyKeyboardRemove()
        bot.reply_to(message, sms)
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
    text: list = callback.data.split(":")[0]
    if text == "name_habit":
        sms1 = "Введите новое название привычки"
        bot.send_message(chat_id, sms1)
        old_name = habit_data_edit["old_name_habit"]
        sms2 = f'Вы уверены что хотите изменить название привычки с "{old_name}" на'
        bot.register_next_step_handler(callback.message, edit_param, text, sms2)
    elif text == "period":
        sms1 = f'Введите дату первого напоминания привычки в формате: {str(datetime.now())[:-7]}'
        bot.send_message(chat_id, sms1)
        sms2 = f'Вы уверены что хотите изменить время отправки смс на'
        bot.register_next_step_handler(callback.message, edit_param, text, sms2)
    elif text == "count_period":
        sms1 = "Сколько раз отправлять уведомления? Введите число не менее 21"
        bot.send_message(chat_id, sms1)
        old_count = habit_data_edit["edit_data"]['count_period']
        sms2 = f'Вы уверены что хотите изменить количество смс с {old_count} на'
        bot.register_next_step_handler(callback.message, edit_param, text, sms2)
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
        try:
            result = requests.get(f"{env.MAIN_HOST}/habit/{message.text}/{chat_id}/")
            if result.status_code == 200:
                sms = f'Введите дату первого напоминания привычки в формате: {str(datetime.now())[:-7]}'
                bot.send_message(chat_id, sms)
                habit_data_edit['edit_data']['name_habit'] = message.text
                habit_state_edit[chat_id] = STATES_EDIT['count_period']
            else:
                raise ValueError
        except ValueError:
            bot.send_message(chat_id, "Введите пожалуйста уникальное название привычки!")
    elif state == STATES_EDIT['count_period']:
        try:
            sms = "Сколько раз отправлять уведомления? Введите число не менее 21"
            result_period: int = validator_period(message.text)
            habit_data_edit['edit_data']['period'] = result_period
            habit_state_edit[chat_id] = STATES_EDIT['end_edit']
            bot.send_message(chat_id, sms)
        except ValueError:
            bot.send_message(chat_id, "Введите пожалуйста коректное значение!")
    elif state == STATES_EDIT['end_edit']:
        try:
            number: int = int(message.text)
            if number < 21:
                raise ValueError
            old_name = habit_data_edit["old_name_habit"]
            habit_data_edit['edit_data']['count_period'] = number
            mark = get_yes_or_no(f"yes:{old_name}", f"no:{old_name}")
            sms = f'Вы уверены что хотите изменить привычку "{old_name}"?'
            bot.send_message(chat_id, sms, reply_markup=mark)
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")


def edit_param(message, key, sms):
    global habit_data_edit
    chat_id, new_param = message.chat.id, message.text
    try:
        result = validator_params({key: new_param}, chat_id)
    except ValueError:
        bot.send_message(chat_id, "Введите пожалуйста коректное значение!")
        bot.register_next_step_handler(message, edit_param, key, sms)
    else:
        old_name = habit_data_edit['old_name_habit']
        habit_data_edit["edit_data"][key] = result
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
        if result.status_code == 202:
            data_habit = json.loads(result.text)
            try:
                old_name: str = data_habit["old_name"]
                new_name: str = data_habit["new_habit"]["name_habit"]
                new_time: int = data_habit["new_habit"]["period"]
            except KeyError:
                sms = "Что то пошло не так"
                bot.send_message(chat_id, sms, reply_markup=mark)
            else:
                cancel_trigger(chat_id, old_name)
                set_cron(chat_id, new_name, new_time)
                sms = f'Ваша привычка "{text[1]}" успешно изменена'
                bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
        habit_data_edit = {"old_name_habit": None, "edit_data": None}
        habit_state_edit[chat_id] = None
    else:
        sms = f'Изменение привычки "{text[1]}" не произошло'
        bot.send_message(chat_id, sms, reply_markup=mark)


"""Обработка неизвестных сообщений"""


@bot.message_handler()
def manage_habits(message):
    bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")
