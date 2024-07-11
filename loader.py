import telebot as tb
from config.environments import env


bot = tb.TeleBot(env.TOKEN)


