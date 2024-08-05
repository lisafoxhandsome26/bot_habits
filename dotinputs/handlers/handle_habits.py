from datetime import datetime

import requests
from telebot import types

from .utils import check_authorization, get_sms_habits, get_sms_for, validator_params, validator_period
from loader import bot
from dotinputs.buttons import get_habits_page, get_authorization_buttons, get_yes_or_no
from dotinputs.scheduler.handle_schedule import set_cron, cancel_trigger
from config.environments import env
from ..database import dao


habit_data: dict = {}
habit_state_edit: dict = {}
habit_state: dict = {}
del_name = "habit_name"
habit_data_edit: dict = {"old_name_habit": None, "edit_data": None}
token: str = "naewfnwaefnsad13223"

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
    hashed = dao.get_hashed_data(chat_id)
    if hashed:
        result = requests.get(
            url=f"{env.MAIN_HOST}list_habit/",
            headers={'Authorization': f'Bearer {hashed.jwt_token}'}
        )
        if result.status_code == 200:
            list_habits = result.json()["habits"]
            sms, mark = get_sms_habits(list_habits)
            bot.send_message(chat_id, sms, reply_markup=mark)
        elif result.status_code == 404:
            sms, mark = "Ваш список привычек еще пуст", get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms, mark = get_authorization_buttons()
            bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


"""Удаление привычки"""


@bot.message_handler(func=lambda message: message.text == "Удалить привычку")
def remove_habits(message):
    global token
    chat_id: int = message.chat.id
    token = dao.get_hashed_data(chat_id)
    if token:
        result = requests.get(
            url=f"{env.MAIN_HOST}list_habit/",
            headers={'Authorization': f'Bearer {token.jwt_token}'}
        )
        if result.status_code == 200:
            list_habits = result.json()["habits"]
            sms, data_del = get_sms_for(list_habits)
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
            bot.send_message(chat_id, "Выберите номер привычки для удаления.")
            bot.register_next_step_handler(message, choice_del_habit, data_del, sms)
        elif result.status_code == 404:
            sms = "Ваш спиок привычек пуст."
            mark = get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms, mark = get_authorization_buttons()
            bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


def choice_del_habit(message, data_del, sms_for_del):
    chat_id = message.chat.id
    global del_name
    try:
        del_name = data_del[int(message.text)]["name_habit"]
        calling_yes = "YES"
        calling_no = "NO"
        mark = get_yes_or_no(calling_yes, calling_no)
        sms = f'Вы уверены что хотите удалить привычку - "{del_name}"?'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        mark = types.ReplyKeyboardRemove()
        sms = "Выберите пожалуйста коректный номер привычки!"
        bot.reply_to(message, sms)
        bot.send_message(chat_id, sms_for_del, reply_markup=mark)
        bot.register_next_step_handler(message, choice_del_habit, data_del, sms_for_del)


@bot.callback_query_handler(
    func=lambda call:
    call.data == "NO" or
    call.data == "YES"
)
def make_delete_habit(call):
    global del_name, token
    chat_id: int = call.message.chat.id
    mark = get_habits_page()
    if call.data == "NO":
        sms = f'Удаление привычки не выполненно.'
        bot.send_message(chat_id, sms, reply_markup=mark)
        token = "asdasdfnidfnasnk"
    else:
        result = requests.delete(
            url=f"{env.MAIN_HOST}habit/",
            json={"name_habit": del_name},
            headers={'Authorization': f'Bearer {token.jwt_token}'}
        )

        if result.status_code == 202:
            cancel_trigger(chat_id, del_name)
            sms = f'Ваша привычка "{del_name}" успешно удалена'
            bot.send_message(chat_id, sms, reply_markup=mark)
            del_name = "name_habit"
            token = "safdasfdasfdas"
        else:
            sms, token = "Что то пошло не так", "dfdfdafafafaf"
            bot.send_message(chat_id, sms, reply_markup=mark)


"""Добавление привычки"""


@bot.message_handler(func=lambda message: message.text == "Добавить привычку")
def add_habits(message):
    global token
    chat_id: int = message.chat.id
    token = check_authorization(chat_id)
    if token != "Авторизоваться" and token is not False:
        habit_state[message.chat.id] = STATES_ADD_HABIT['name_habit']
        mark = types.ReplyKeyboardRemove()
        bot.send_message(chat_id, "Введите название привычки", reply_markup=mark)
        bot.register_next_step_handler(message, add_habit)
    elif token == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


@bot.message_handler(func=lambda message: message.chat.id in habit_state)
def add_habit(message):
    global habit_data, token
    chat_id = message.chat.id
    state = habit_state[chat_id]
    if state == STATES_ADD_HABIT['name_habit']:
        try:
            result = requests.get(
                url=f"{env.MAIN_HOST}habit/",
                json={"habit_name": message.text},
                headers={'Authorization': f'Bearer {token}'}
            )
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
                url=f"{env.MAIN_HOST}habit/",
                json={"data_habit": habit_data},
                headers={'Authorization': f'Bearer {token}'}
            )
            name_habit = habit_data["name_habit"]
            new_time = habit_data["period"]
            set_cron(chat_id, name_habit, new_time)

            del habit_state[chat_id]
            token, habit_data = "dadadsadad123646", {}
            sms, mark = "Твоя привычка успешно добавлена", get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)


"""Изменение привычки"""


@bot.message_handler(func=lambda message: message.text == "Изменить привычку")
def edit_habits(message):
    global token
    chat_id: int = message.chat.id
    token = check_authorization(chat_id)
    if token != "Авторизоваться" and token is not False:
        result = requests.get(
            url=f"{env.MAIN_HOST}list_habit/",
            headers={'Authorization': f'Bearer {token}'}
        )
        if result.status_code == 200:
            list_habits = result.json()["habits"]
            sms, data_edit = get_sms_for(list_habits)
            mark = types.ReplyKeyboardRemove()
            bot.send_message(chat_id, sms, reply_markup=mark)
            bot.send_message(chat_id, "Выберите номер привычки для изменения.")
            bot.register_next_step_handler(message, choice_edit_habit, data_edit, sms)
        else:
            sms = "Ваш список привычек пуст."
            mark = get_habits_page()
            bot.send_message(chat_id, sms, reply_markup=mark)
    elif token == "Авторизоваться":
        sms, mark = get_authorization_buttons()
        bot.send_message(chat_id, sms, reply_markup=mark)
    else:
        bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")


def choice_edit_habit(message, data_edit, sms_for_edit):
    chat_id: int = message.chat.id
    try:
        global habit_data_edit
        habit = data_edit[int(message.text)]
        edit_name = habit['name_habit']
        habit_data_edit['edit_data'] = habit
        habit_data_edit["old_name_habit"] = edit_name

        mark = types.InlineKeyboardMarkup()
        name = types.InlineKeyboardButton("Название", callback_data="name_habit")
        period = types.InlineKeyboardButton("Период", callback_data="period")
        count_period = types.InlineKeyboardButton("Количество смс", callback_data="count_period")
        all_params = types.InlineKeyboardButton("Все параметры", callback_data="all_params")
        mark.row(name, count_period)
        mark.row(period, all_params)

        sms = f'Вы выбрали для изменения привычку - "{edit_name}". Вебирите параметр'
        bot.send_message(chat_id, sms, reply_markup=mark)
    except (ValueError, KeyError):
        sms, mark = f"Выберите пожалуйста коректный номер привычки!", types.ReplyKeyboardRemove()
        bot.reply_to(message, sms)
        bot.send_message(chat_id, sms_for_edit, reply_markup=mark)
        bot.register_next_step_handler(message, choice_edit_habit, data_edit, sms_for_edit)


@bot.callback_query_handler(
    func=lambda call:
    call.data == "name_habit" or
    call.data == "period" or
    call.data == "count_period" or
    call.data == "all_params"
)
def callback_edit(call):
    chat_id: int = call.message.chat.id

    if call.data == "name_habit":
        sms1 = "Введите новое название привычки"
        bot.send_message(chat_id, sms1)
        old_name = habit_data_edit["old_name_habit"]
        sms2 = f'Вы уверены что хотите изменить название привычки с "{old_name}" на'
        bot.register_next_step_handler(call.message, edit_param, call.data, sms2)

    elif call.data == "period":
        sms1 = f'Введите дату первого напоминания привычки в формате: {str(datetime.now())[:-7]}'
        bot.send_message(chat_id, sms1)
        sms2 = f'Вы уверены что хотите изменить время отправки смс на'
        bot.register_next_step_handler(call.message, edit_param, call.data, sms2)

    elif call.data == "count_period":
        sms1 = "Сколько раз отправлять уведомления? Введите число не менее 21"
        bot.send_message(chat_id, sms1)
        old_count = habit_data_edit["edit_data"]['count_period']
        sms2 = f'Вы уверены что хотите изменить количество смс с {old_count} на'
        bot.register_next_step_handler(call.message, edit_param, call.data, sms2)

    else:
        habit_state_edit[chat_id] = STATES_EDIT['name_habit']
        sms = "Введите новое название привычки"
        bot.send_message(chat_id, sms)
        edit_all_params(call.message)


@bot.message_handler(func=lambda message: message.chat.id in habit_state_edit)
def edit_all_params(message):
    global habit_data_edit, token
    chat_id: int = message.chat.id
    state = habit_state_edit[chat_id]
    if state == STATES_EDIT['name_habit']:
        habit_state_edit[chat_id] = STATES_EDIT['period']
    elif state == STATES_EDIT['period']:
        try:
            result = requests.get(
                url=f"{env.MAIN_HOST}/habit/",
                json={"habit_name": message.text},
                headers={'Authorization': f'Bearer {token}'}
            )
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
            mark = get_yes_or_no("yes", "no")
            sms = f'Вы уверены что хотите изменить привычку "{old_name}"?'
            bot.send_message(chat_id, sms, reply_markup=mark)
        except ValueError:
            bot.send_message(chat_id, f"Введите пожалуйста целое число!")


def reset_params(chat_id):
    global habit_data_edit, habit_state_edit, token
    habit_data_edit = {"old_name_habit": None, "edit_data": None}
    habit_state_edit[chat_id] = None
    token = "dfcdfcsdfcdfcdf"


def edit_param(message, key, sms):
    global habit_data_edit, token
    chat_id, new_param = message.chat.id, message.text
    try:
        result = validator_params({key: new_param}, token)
    except ValueError:
        bot.send_message(chat_id, "Введите пожалуйста коректное значение!")
        bot.register_next_step_handler(message, edit_param, key, sms)
    else:
        habit_data_edit["edit_data"][key] = result
        mark = get_yes_or_no(f"yes", f"no")
        sms += f" {new_param}?"
        bot.send_message(chat_id, sms, reply_markup=mark)


@bot.callback_query_handler(
    func=lambda call:
    call.data == "no" or
    call.data == "yes"
)
def make_edit_habit(call):
    global habit_data_edit, habit_state_edit, token
    chat_id: int = call.message.chat.id
    mark = get_habits_page()
    if call.data == "yes":
        result = requests.patch(
            url=f"{env.MAIN_HOST}habit/",
            json=habit_data_edit,
            headers={'Authorization': f'Bearer {token}'}
        )
        if result.status_code == 202:
            data_habit = result.json()
            try:
                new_name: str = data_habit["new_habit"]["name_habit"]
                new_time: int = data_habit["new_habit"]["period"]
            except KeyError:
                sms = "Что то пошло не так"
                bot.send_message(chat_id, sms, reply_markup=mark)
            else:
                edit_name = habit_data_edit["old_name_habit"]
                cancel_trigger(chat_id, edit_name)
                set_cron(chat_id, new_name, new_time)
                sms = f'Ваша привычка "{edit_name}" успешно изменена'
                bot.send_message(chat_id, sms, reply_markup=mark)
        else:
            sms = "Что то пошло не так"
            bot.send_message(chat_id, sms, reply_markup=mark)
        reset_params(chat_id)
    else:
        sms = f'Изменение привычки не произошло'
        bot.send_message(chat_id, sms, reply_markup=mark)
        reset_params(chat_id)


"""Обработка неизвестных сообщений"""


@bot.message_handler()
def manage_habits(message):
    bot.reply_to(message, "Я не понимаю что вы ввели, введите /start")
