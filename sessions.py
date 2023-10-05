import threading
import time
from next_step_handlers import set_answer
from telebot import types
from users import Admin, Gamer
from kahoot_bot import bot


SYMBOLS = '🔺⚫⬜🔷'


class Session:
    def __init__(
            self,
            session_id,
            admin: Admin,
            gamer_list: list[Gamer] = None
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

    @staticmethod
    def find_session_by_admin(admin_id, sessions):
        for session in sessions:
            if str(session.admin.user_id) == str(admin_id):
                return session

    def start_game(self, message):
        gamer_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        gamer_markup.add(*[types.InlineKeyboardButton(char) for char in SYMBOLS])

        for gamer in self:
            msg = bot.send_message(gamer.user_id, 'Игра началась!', reply_markup=gamer_markup)
            gamer.msg = msg
            bot.register_next_step_handler(msg, set_answer, gamer=gamer)

        for num, task in enumerate(self.kahoot_file):
            for gamer in self.gamer_list:
                gamer.selected_option = None
                gamer.score_growth = 0

            message_header = f'Вопрос {num + 1}/{len(self.kahoot_file)}. (0/{len(self.gamer_list)}) \n'
            message_question = f'{task.question}\n'
            options = dict(zip(SYMBOLS, task.options))

            message_body = ''
            for sym, option in options.items():
                message_body += f'    {sym} {option}\n'

            message_text = message_header + message_question + message_body
            if self.question_area is None:
                question_message = bot.send_message(self.admin.user_id, message_text)
                self.question_area = question_message.message_id
            else:
                bot.edit_message_text(
                    text=message_text,
                    chat_id=message.chat.id,
                    message_id=self.question_area
                )

            for gamer in self:
                bot.register_next_step_handler(gamer.msg, set_answer, gamer=gamer)

            start_time = time.time()
            out_time = 10

            while time.time() - start_time <= 10:
                answered_gamers = []

                for gamer in self:
                    if gamer.selected_option is not None:

                        if gamer.answer_time is None:
                            gamer.answer_time = round(10 - (time.time() - start_time), 3)

                        answered_gamers.append(True)

                    else:
                        answered_gamers.append(False)

                message_header = (f'Вопрос {num + 1}/{len(self.kahoot_file)}. '
                                  f'({answered_gamers.count(True)}/{len(self.gamer_list)}) \n')
                message_text = message_header + message_question + message_body

                if all(answered_gamers):
                    break

                if out_time != (10 - int(time.time() - start_time)):
                    out_time = 10 - int(time.time() - start_time)
                    bot.edit_message_text(
                        text=f'{message_text}\nОставшееся время: {out_time}',
                        chat_id=message.chat.id,
                        message_id=self.question_area
                    )

            answers = []

            for gamer in self:
                if gamer.selected_option is not None:
                    selected_option = options[gamer.selected_option]

                    if task.correct_answer == selected_option:
                        gamer.score_growth = int(1000 * (1 + (gamer.answer_time / 10)))
                        gamer.score += gamer.score_growth

                    answers.append(selected_option)

            true_answer_string = f'Правильный ответ: {task.correct_answer}\n'

            for sym, option in options.items():
                stats = answers.count(option)
                true_answer_string += f'За {option} ({sym}) проголосовали {stats}\n'

            self.admin.create_keyboard()
            bot.edit_message_text(
                text=f'{message_text}\n{true_answer_string}',
                chat_id=message.chat.id,
                message_id=self.question_area,
                reply_markup=self.admin.keyboard,
            )

            admin_action_waiting_event = threading.Event()
            self.admin.event = admin_action_waiting_event
            admin_action_waiting_event.wait()
