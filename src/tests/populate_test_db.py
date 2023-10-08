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



users_2 = ['User_1', 'User_2', 'User_3', 'User_4']
name_lobby_2 = "1234_lobby"

def load_users_for_test_start_and_end_game():

    with db_session:
        if count(User.select()) == 4:
            for name in users_2:
                User(name=name)

@db_session
def load_lobby_and_game_for_test_start_and_end_game():

    with db_session:
        if count(Lobby.select()) == 1:
            Lobby(name=name_lobby_2, min_players=4, max_players=5, host="User_2")

def load_users_2_in_lobby_2():

    with db_session:
        for name in users_2:
            user = User.get(name=name)
            user.lobby = Lobby['1234_lobby']


if __name__ == '__main__':
    load_users_for_test()
    load_lobby_for_test()

    # datos para testear el end game
    load_users_for_test_start_and_end_game()
    load_lobby_and_game_for_test_start_and_end_game()
    load_users_2_in_lobby_2()
