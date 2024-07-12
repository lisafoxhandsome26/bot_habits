from backend.run_fastapi import get_application, lifespan
from loader import bot
from dotinputs import handlers

app = get_application(lifespan)

if __name__ == "__main__":
    print("Запуск Бота для трекинга привычек")
    bot.polling(non_stop=True)
