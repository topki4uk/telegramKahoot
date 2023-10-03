import threading
from random import randint
import time
from next_step_handlers import set_answer, next_question
from telebot import types, TeleBot
from users import User, Admin

SYMBOLS = '🔺⚫⬜🔷'


class Session:
    def __init__(
            self,
            session_id,
            admin: Admin,
            gamer_list: list[User] = None
    ):
        self.session_id = session_id
        self.admin = admin
        self.kahoot_file = None

        self.wait = False

        if gamer_list is None:
            self.gamer_list = []
        else:
            self.gamer_list = gamer_list

    def __add__(self, other):
        self.gamer_list.append(other)
        return self

    def enable_keyboard(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.InlineKeyboardButton(char) for char in SYMBOLS)

        for gamer in self:
            gamer.keyboard = markup

    def disable_keyboard(self):
        for gamer in self:
            gamer.keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    def __getitem__(self, item):
        return self.gamer_list[item]

    def __iter__(self):
        return iter(self.gamer_list)

    def start_game(self, bot: TeleBot, message):
        gamer_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        gamer_markup.add(*[types.InlineKeyboardButton(char) for char in SYMBOLS])

        for num, task in enumerate(self.kahoot_file):
            string_message = f'Вопрос {num + 1}/{len(self.kahoot_file)}.\n'
            string_message += f'{task.question}\n'
            options = dict(zip(SYMBOLS, task.options))

            with open(r'10-seconds.gif', 'rb') as file:
                bot.send_animation(message.chat.id, file)

            for sym, option in options.items():
                string_message += f'    {sym} {option}\n'

            bot.send_message(self.admin.user_id, string_message)

            for gamer in self:
                msg = bot.send_message(gamer.user_id, string_message, reply_markup=gamer_markup)
                bot.register_next_step_handler(msg, set_answer, options=options, gamer=gamer)

            time.sleep(10)

            answers = [gamer.selected_option for gamer in self.gamer_list]
            true_answer_string = f'Правильный ответ: {task.correct_answer}\n'

            for sym, option in options.items():
                stats = answers.count(option)
                true_answer_string += f'За {option} ({sym}) проголосовали {stats}\n'

            msg_admin = bot.send_message(self.admin.user_id, true_answer_string)

            admin_action_waiting_event = threading.Event()

            bot.register_next_step_handler(
                msg_admin,
                next_question,
                event=admin_action_waiting_event
            )
            admin_action_waiting_event.wait()


def main():
    admin = User('1', 'ADMIN', 'name')
    session = Session('1', admin)

    for i in range(10):
        user = User(randint(1, 1000), 'default', f'user{i}')
        session += user

    for user in session:
        print(user.user_id)


if __name__ == '__main__':
    main()
