from pony.orm import db_session, count

from models import *

users_for_test = ['User_A', 'User_B', 'User_C', 'User_D']
name_lobby = "ABCD_lobby"

@db_session
def load_users_for_test():

    with db_session:
        if count(User.select()) == 0:
            for name in users_for_test:
                User(name=name)

@db_session
def load_lobby_for_test():

    with db_session:
        if count(Lobby.select()) == 0:
            Lobby(name=name_lobby, min_players=4, max_players=5, host="User_A")

if __name__ == '__main__':
    load_users_for_test()
    load_lobby_for_test()
