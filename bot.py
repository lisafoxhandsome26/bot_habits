from loader import bot
from dotinputs.scheduler.core import scheduler
from dotinputs import handlers

if __name__ == "__main__":
    scheduler.start()
    bot.polling(non_stop=True)
