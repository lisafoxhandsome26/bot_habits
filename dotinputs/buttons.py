from telebot import types


def get_habits_page():
    """Кнопки для вкладки привычек"""
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Перейти на статус привычек")
    bt2 = types.KeyboardButton("Удалить привычку")
    bt3 = types.KeyboardButton("Изменить привычку")
    bt4 = types.KeyboardButton("Добавить привычку")
    bt5 = types.KeyboardButton("Вернуться назад")
    mark.row(bt1, bt2)
    mark.row(bt3, bt4)
    mark.row(bt5)
    return mark


def get_profile_buttons():
    """Кнопки для основной вкладки"""
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Узнать инфо о себе")
    bt2 = types.KeyboardButton("Вкладка с привычками")
    bt3 = types.KeyboardButton("Выйти из своего профиля")
    mark.row(bt1)
    mark.row(bt2, bt3)
    return mark


def get_authorization_buttons():
    """Кнопка для авторизации пользователя"""
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bt1 = types.KeyboardButton("Авторизоваться")
    mark.add(bt1)
    sms = "Чтобы продолжить вам необходимо авторизоваться!"
    return sms, mark


def get_yes_or_no(calling_yes: str, calling_no: str):
    """Кнопки для подтверждения выполняемого действия"""
    mark = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton("Да", callback_data=calling_yes)
    no = types.InlineKeyboardButton("Нет", callback_data=calling_no)
    mark.row(yes, no)
    return mark
