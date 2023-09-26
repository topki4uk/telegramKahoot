from telebot import TeleBot
from random import randint
from fnmatch import fnmatch
from sessions import Session, User
import os

token = os.environ.get('TELEGRAM_TOKEN')
bot = TeleBot(token)
sessions = []


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ ")


@bot.message_handler(commands=['function'])
def some_message(message):
    bot.send_message(message.chat.id, 'Какое-то сообщение...')


@bot.message_handler(commands=['create_session'])
def create_session(message):
    user_id = str(message.from_user.id)

    for session in sessions:
        if str(session.admin) == user_id:
            bot.send_message(message.chat.id, 'Ваша сессия уже существует!')
            return

    session_id = f'{randint(100, 999)}-{randint(100, 999)}-{randint(100, 999)}'
    admin = User(
        message.from_user.id,
        'ADMIN',
        user_id
    )
    session = Session(session_id, admin)
    sessions.append(session)

    with open(r'text_messages/new_session_message.txt', 'r', encoding='utf8') as text:
        text_message = f'{text.read()} {session_id}'

    bot.send_message(message.chat.id, text_message)


@bot.message_handler(commands=['get_session_info'])
def session_info(message):
    admins = {str(session.admin): session.session_id for session in sessions}
    bot.send_message(message.chat.id, str(admins))


@bot.message_handler(commands=['join_session'], content_types=['text'])
def join_session(message):
    msg = bot.send_message(message.chat.id, 'Введите номер сессии!')

    bot.register_next_step_handler(msg, input_session_id)


def input_session_id(message):
    resp = message.text
    user_id = str(message.from_user.id)

    if fnmatch(str(resp), '???-???-???'):
        for session in sessions:
            if session.session_id == str(resp):
                user = User(user_id, 'Gamer', user_id)
                if user in session.gamer_list:
                    bot.send_message(message.chat.id, 'Вы уже подключены к сессии!')
                    return

                session += user
                bot.send_message(message.chat.id, 'Подключение произошло успешно!')
                return
        else:
            bot.send_message(message.chat.id, 'Данная сессия не найдена!')
            return
    else:
        bot.send_message(message.chat.id, 'Некорректный номер сессии!')
        return


bot.polling(none_stop=True)
