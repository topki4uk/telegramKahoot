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
        self.question_area = None

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

        start_msg = None
        for gamer in self:
            start_msg = bot.send_message(gamer.user_id, 'Игра началась!', reply_markup=gamer_markup)
            bot.register_next_step_handler(start_msg, set_answer, gamer=gamer)

        for num, task in enumerate(self.kahoot_file):
            string_message = f'Вопрос {num + 1}/{len(self.kahoot_file)}.\n'
            string_message += f'{task.question}\n'
            options = dict(zip(SYMBOLS, task.options))

            for sym, option in options.items():
                string_message += f'    {sym} {option}\n'

            if self.question_area is None:
                question_message = bot.send_message(self.admin.user_id, string_message)
                self.question_area = question_message.message_id
            else:
                bot.edit_message_text(
                    text=string_message,
                    chat_id=message.chat.id,
                    message_id=self.question_area
                )

            for gamer in self:
                bot.register_next_step_handler(start_msg, set_answer, gamer=gamer)

            start_time = time.time()
            out_time = 10

            while time.time() - start_time <= 10:
                if out_time != (10 - int(time.time() - start_time)):
                    out_time = 10 - int(time.time() - start_time)
                    bot.edit_message_text(
                        text=f'{string_message}\nОставшееся время: {out_time}',
                        chat_id=message.chat.id,
                        message_id=self.question_area
                    )

            answers = [options[gamer.selected_option] for gamer in self.gamer_list]
            true_answer_string = f'Правильный ответ: {task.correct_answer}\n'

            for sym, option in options.items():
                stats = answers.count(option)
                true_answer_string += f'За {option} ({sym}) проголосовали {stats}\n'

            admin_action_waiting_event = threading.Event()
            self.admin.event = admin_action_waiting_event
            self.admin.create_keyboard()

            bot.edit_message_text(
                text=f'{string_message}\n\n{true_answer_string}',
                chat_id=message.chat.id,
                message_id=self.question_area,
                reply_markup=self.admin.keyboard,
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
