import time

from users import Gamer


def set_answer(message, options, gamer):

    for sym, option in options.items():
        if message.text == sym:
            gamer.selected_option = option


def next_question(message, session, e):
    print(message.text)
    if message.text == '/next':
        e.set()
