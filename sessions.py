from random import randint
import time
import threading


class User:
    def __init__(self, user_id, status, name):
        self.user_id = user_id
        self.msg = None
        self.status = status
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return True if (self.user_id == other.user_id) else False

    def find_session(self, sessions):
        for session in sessions:
            if str(session.admin) == str(self.user_id):
                return session


class Session:
    def __init__(
            self,
            session_id,
            admin: User,
            gamer_list: list[User] = None
    ):
        self.session_id = session_id
        self.admin = admin
        self.kahoot_file = None

        self.time = 0

        if gamer_list is None:
            self.gamer_list = []
        else:
            self.gamer_list = gamer_list

    def __add__(self, other):
        self.gamer_list.append(other)
        return self

    def timer(self, n):
        self.time = n
        t_start = time.time()
        current_t = time.time()

        while int(current_t - t_start) < n:
            current_t = time.time()
            self.time = n - int(current_t - t_start)

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
