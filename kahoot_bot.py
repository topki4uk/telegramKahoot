import os
from telebot import TeleBot


token = os.environ.get('TELEGRAM_TOKEN')
bot = TeleBot(token)
