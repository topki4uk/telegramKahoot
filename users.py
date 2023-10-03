import telebot

from next_step_handlers import next_question


class User (object):
    def __init__(self, message):
        self.user_id = message.from_user.id
        self.msg = None
        self.selected_option = None
        self.keyboard = None
        self.last_name = f'{message.from_user.last_name}'
        self.first_name = f'{message.from_user.first_name}'
        self.full_name = f'{self.last_name} {self.first_name}'

    def __str__(self):
        return self.full_name

    def __eq__(self, other):
        return True if (self.user_id == other.user_id) else False

    def find_session(self, sessions):
        for session in sessions:
            if session.admin == self:
                return session


class Admin (User):
    def __init__(self, message):
        super().__init__(message)
        self.status = 'ADMIN'
        self.event = None
        self.button_data = {
            'Следующий вопрос': 'next',
        }

    def create_keyboard(self):
        self.keyboard = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton('Следующий вопрос', callback_data='text')
        j_button = {**button.to_dict(), 'event': id(self.event)}
        self.keyboard.add(
            telebot.types.InlineKeyboardButton().de_json(j_button)
        )


class Gamer (User):
    def __init__(self, message):
        super().__init__(message)
        self.status = 'GAMER'
