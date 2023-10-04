import threading

import telebot.types
from telebot import TeleBot, types
from random import randint
from fnmatch import fnmatch

from sessions import Session
from serelize import KHTFile

from users import Gamer, Admin
from kahoot_bot import bot


SYMBOLS = '🔺⚫⬜🔷'
sessions = []


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    create = types.KeyboardButton("/create_session")
    session_info_button = types.KeyboardButton('/get_session_info')
    add_file_button = types.KeyboardButton('/set_file')
    join_button = types.KeyboardButton('/join_session')
    start_game_button = types.KeyboardButton('/start_game')

    markup.add(create, add_file_button, join_button,
               start_game_button, session_info_button)

    bot.send_message(message.chat.id, "Привет ✌️", reply_markup=markup)


@bot.message_handler(commands=['function'])
def some_message(message):
    bot.send_message(message.chat.id, 'Какое-то сообщение...')


@bot.callback_query_handler(func=lambda q: q.data == 'text')
def next_question(callback_query: telebot.types.CallbackQuery):
    session = Session.find_session_by_admin(callback_query.from_user.id, sessions)

    if session is not None:
        session.admin.event.set()
    else:
        print('Not found!')


@bot.message_handler(commands=['create_session'])
def create_session(message):
    admin = Admin(message)

    for session in sessions:
        if session.admin == admin:
            bot.send_message(message.chat.id, 'Ваша сессия уже существует!')
            return

    session_id = f'{randint(100, 999)}'
    session = Session(session_id, admin)
    sessions.append(session)

    with open(r'text_messages/new_session_message.txt', 'r', encoding='utf8') as text:
        text_message = f'{text.read()} {session_id}'

    bot.send_message(message.chat.id, text_message)


@bot.message_handler(commands=['get_session_info'])
def session_info(message):
    admin = Admin(message)

    session_info_message = ''
    session = admin.find_session(sessions)

    if session is None:
        bot.send_message(message.chat.id, 'У вас нет активных сессий!')
        return

    session_info_message += f'Номер сессии: {session.session_id}\n'
    session_info_message += f'Админ сессии: {session.admin}\n\n'
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

    if fnmatch(str(resp), '???'):
        for session in sessions:
            if session.session_id == str(resp):
                gamer = Gamer(message)
                if gamer in session.gamer_list:
                    bot.send_message(message.chat.id, 'Вы уже подключены к сессии!')
                    return

                session += gamer
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
    admin = Admin(message)

    session = admin.find_session(sessions)

    if session is None:
        bot.send_message(message.chat.id, 'Не найдены активные сессии!')
        return

    game_thread = threading.Thread(target=session.start_game, args=(message, ))
    game_thread.start()


@bot.message_handler(commands=['set_file'], content_types=['text', ])
def set_test_file(message: telebot.types.Message):
    msg = bot.send_message(message.chat.id, 'Пришлите файл с расширением .json для вашей игры.')
    bot.register_next_step_handler(msg, send_file)


def send_file(message: types.Message):
    resp = message.document

    if message.content_type != 'document':
        bot.send_message(message.chat.id, 'Это не файл!')
        return

    if 'json' not in str(resp.file_name).rsplit('.', maxsplit=1):
        bot.send_message(message.chat.id, 'Неверное расширение файла!')
        return

    admin = Admin(message)

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
