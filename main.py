import time

from telebot import TeleBot, types
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    create = types.KeyboardButton("/create_session")
    add_file_button = types.KeyboardButton('/set_file')
    join_button = types.KeyboardButton('/join_session')
    start_game_button = types.KeyboardButton('/start_game')

    markup.add(create, add_file_button, join_button, start_game_button)

    bot.send_message(message.chat.id, "Привет ✌️", reply_markup=markup)


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

    for num, task in enumerate(session.kahoot_file):
        string_message = f'Вопрос {num+1}/{len(session.kahoot_file)}.\n'
        string_message += f'{task.question}\n'

        for i, option in enumerate(task.options):
            string_message += f'    {i+1}. {option}\n'

        for gamer in session:

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = [
                types.KeyboardButton(char) for char in '🔺⚫⬜🔷'
            ]
            markup.add(*buttons)

            with open(r'10-seconds.gif', 'rb') as file:
                bot.send_animation(gamer.user_id, file)

            msg = bot.send_message(gamer.user_id, string_message, reply_markup=markup)
            bot.register_next_step_handler(msg, set_answer)

        time.sleep(10)


def set_answer(message):
    if message.text == '🔺':
        ...
    elif message.text == '⚫':
        ...
    elif message.text == '⬜':
        ...
    elif message.text == '🔷':
        ...


@bot.message_handler(commands=['set_file'], content_types=['text', ])
def set_test_file(message):
    msg = bot.send_message(message.chat.id, 'Пришлите файл с расширением .json для вашей игры.')
    bot.register_next_step_handler(msg, send_file)


def send_file(message):
    resp = message.document

    if 'json' not in str(resp.file_name).rsplit('.', maxsplit=1):
        bot.send_message(message.chat.id, 'Неверное расширение файла!')
        return

    admin = User(
        message.from_user.id,
        'Admin',
        f'{message.from_user.last_name} {message.from_user.first_name}'
    )

    session = admin.find_session(sessions)

    if session is None:
        bot.send_message(message.chat.id, 'Не найдены активные сессии!')
        return

    file = bot.get_file(resp.file_id)
    kahoot_file = bot.download_file(file.file_path).decode('utf8')
    session.kahoot_file = KHTFile(kahoot_file)

    bot.send_message(message.chat.id, 'Файл успешно загружен!')
    bot.send_message(message.chat.id,
                     f'''Название файла: {session.kahoot_file.title}\nКоличество вопросов: {len(session.kahoot_file)}'''
                     )


bot.polling(none_stop=True)
