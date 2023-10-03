SYMBOLS = '🔺⚫⬜🔷'


def set_answer(message, gamer):
    for sym in SYMBOLS:
        if message.text == sym:
            gamer.selected_option = sym


def next_question(message, event):
    if message.text == '/next':
        event.set()
