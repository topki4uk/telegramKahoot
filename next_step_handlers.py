def set_answer(message, options, gamer):
    for sym, option in options.items():
        if message.text == sym:
            gamer.selected_option = option


def next_question(message, event):
    print(message.text)
    if message.text == '/next':
        event.set()
