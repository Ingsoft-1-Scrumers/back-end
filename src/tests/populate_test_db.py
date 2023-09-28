from pony.orm import db_session, count

from models import User


@db_session
def load_data_for_test():
    users = ['User_A', 'User_B']

    with db_session:
        if count(User.select()) == 0:
            for name in users:
                User(name=name)


if __name__ == '__main__':
    load_data_for_test()
