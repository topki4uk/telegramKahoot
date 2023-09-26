import threading
from random import randint


class User:
    def __init__(self, user_id, status, name):
        self.user_id = user_id
        self.status = status
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return True if (self.user_id == other.user_id) else False


class Session:
    def __init__(
            self,
            session_id,
            admin: User,
            gamer_list: list[User] = None
    ):
        self.session_id = session_id
        self.admin = admin

        if gamer_list is None:
            self.gamer_list = []
        else:
            self.gamer_list = gamer_list

    def __add__(self, other):
        self.gamer_list.append(other)
        return self

    def __getitem__(self, item):
        return self.gamer_list[item]

    def __iter__(self):
        return iter(self.gamer_list)


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
