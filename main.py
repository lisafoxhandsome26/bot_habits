from backend.run_fastapi import get_application, lifespan
#from loader import bot
#from dotinputs import handlers


app = get_application(lifespan)
#bot.polling(non_stop=True)


# from asyncio import run
# from shemases.shemases import UserSchema, HabitSchema
# from database.dao import (
#     create_users,
#     create_tables,
#     get_all_data_user,
#     add_user,
#     add_habit,
#     delete_habit,
#     get_list_habit,
#     edit_habit,
#     authenticated
# )


# data = {
#         "fullname": "Богдан Миронович",
#         "age": 30,
#         "location": "Светлодарск",
#         "purpose": "Улучшить свою жизнь",
#         "why": "Хочу быть счастливым",
#         "hobby": "Увлекаюсь компьютерами, машинами, и девушками",
#         "chat_id": 921946875,
#         "authorization": True,
#         "habits": []
#     }
# data_habit = {
#     "name_habit": 'Бросить курить',
#     'period': 125647,
#     'count_period': 10
# }
#
# edit_data_habit = {
#     "name_habit": 'Бросить пить',
#     'period': 125647566,
#     'count_period': 15
# }
#run(create_tables()) # Создать таблицы
#run(create_users()) # Создать тестового пользователя
#run(add_user(data)) # Добавить пользователя
#run(authenticated(message_id=921946875, status=False)) # Выйти из профиля пользователя
#run(add_habit(message_id=921946875, data_habit=data_habit)) #Добавить привычку
#run(edit_habit(message_id=921946875, old_name_habit="Бросить курить", edit_data=edit_data_habit)) #Редактировать привычку
#run(delete_habit(message_id=921946875, name_habit="Бросить пить")) #Удалить Привычку
#obj = run(get_all_data_user(message_id=921946875)) # Получить данные о пользователе
# list_obj = run(get_list_habit(message_id=921946875)) # Получить спиок привычек
#
# data = [HabitSchema.model_validate(obj, from_attributes=True).dict() for obj in list_obj] # Сериализация списка привычек
# print(data)




