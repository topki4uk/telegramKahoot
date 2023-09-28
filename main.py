from telebot import TeleBot
from random import randint
from fnmatch import fnmatch
from sessions import Session, User
from serelize import KHTFile
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
    user = User(
        message.from_user.id,
        'Admin',
        f'{message.from_user.last_name} {message.from_user.first_name}'
    )

    session_info_message = ''
    session = user.find_session(sessions)

    if session is None:
        bot.send_message(message.chat.id, 'У вас нет активных сессий!')
        return

    session_info_message += f'Номер сессии: {session.session_id}\n'
    session_info_message += f'Список игроков:\n'

    for gamers in session:
        session_info_message += f'{gamers}\n'

    bot.send_message(message.chat.id, session_info_message)


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


@bot.message_handler(commands=['start_game'])
def start_game(message):
    admin = User(
        message.from_user.id,
        'Admin',
        f'{message.from_user.last_name} {message.from_user.first_name}'
    )

    session = admin.find_session(sessions)

    if session is None:
        bot.send_message(message.chat.id, 'Не найдены активные сессии!')
        return

    for gamer in session:
        bot.send_message(gamer.user_id, 'Kot')


@bot.message_handler(commands=['set_file'], content_types=['text', ])
def set_test_file(message):
    msg = bot.send_message(message.chat.id, 'Пришлите файл с расширением .kht для вашей игры.')
    bot.register_next_step_handler(msg, send_file)


def send_file(message):
    resp = message.document
    file = bot.get_file(resp.file_id)
    download_file = bot.download_file(file.file_path)

    kht = KHTFile(download_file.decode('utf8'))

    bot.send_message(message.chat.id, str(kht.tasks))


bot.polling(none_stop=True)
