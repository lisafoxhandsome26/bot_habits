user_state = {}
habit_state = {}

STATES = {
    'introduction': 'introduction',
    'fullname': 'fullname',
    'age': 'age',
    'location': 'location',
    'purpose': 'purpose',
    'why': 'why',
    'hobby': 'hobby',
    'register': 'register'
}

STATES_ADD_HABIT = {
    "name_habit": 'name_habit',
    'period': 'period',
    'count_period': 'count_period'
}

user_data: dict = {}
habit_data: dict = {}
DATA_USER = [
    {
        "fullname": "Александр Сергеев",
        "age": 27,
        "location": "смт Луганское",
        "purpose": "Улучшить свою жизнь",
        "why": "Хочу быть счастливым",
        "hobby": "Увлекаюсь компьютерами, машинами, и девушками",
        "chat_id": 921946846,
        "authorization": True,
        "habits": []
    }
]
