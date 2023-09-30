from models import User, Lobby, Game
from pony.orm import db_session

class UserRepository:

    @db_session
    def create_user(self, user_name: str):
        User(name=user_name)

    @db_session
    def get_user(self, user_name: str):
        user = User.get(name=user_name)
        if user is None:
            raise ValueError("User does not exist with name: {}".format(user_name))
        return user

    @db_session
    def user_exists(self, user_name: str) -> bool:
        return User.exists(name=user_name)
    
    @db_session
    def is_user_in_a_lobby(self, user_name: str) -> bool:
        user = User.get(name=user_name)
        return user.lobby is not None
    
    @db_session
    def is_user_in_lobby(self, lobby_name: str, user_name: str) -> bool:
        lobby_repo = LobbyRepository()
        lobby = lobby_repo.get_lobby(lobby_name)
        users_dict = [{'name': user.name} for user in lobby.users]
        result = False
        for user in users_dict:
            if user['name'] == user_name:
                result = True
        return result
    
    @db_session
    def is_user_host(self, lobby_name: str, user_name: str) -> bool:
        lobby_repo = LobbyRepository()
        lobby = lobby_repo.get_lobby(lobby_name)
        return lobby.host.name == user_name


class LobbyRepository:

    @db_session
    def create_lobby(self, lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
        user_repo = UserRepository()
        host = user_repo.get_user(host_name)
        if (password == ''):
            password = None   
        lobby = Lobby(name=lobby_name, min_players=min_players, max_players=max_players, password=password, host=host) # No es necesario modificar el atributo hosting_lobby del usuario, se hace automáticamente
        lobby.users.add(host) # No es necesario modificar el atributo lobby del usuario, se hace automáticamente

    @db_session
    def get_lobby(self, lobby_name: str):
        lobby = Lobby.get(name=lobby_name)
        if lobby is None:
            raise ValueError("Lobby does not exist with name: {}".format(lobby_name))
        return lobby

    @db_session 
    def lobby_exists(self, lobby_name: str) -> bool:
        return Lobby.exists(name=lobby_name)
    
    @db_session
    def is_lobby_full(self, lobby_name: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        return len(lobby.users) == lobby.max_players
    
    @db_session
    def is_password_correct(self, lobby_name: str, password: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        if lobby.password is None:
            result = True
        else:
            result = lobby.password == password
        return result

    @db_session
    def add_user_to_lobby(self, lobby_name: str, user_name : str):
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        lobby = Lobby.get(name=lobby_name)
        lobby.users.add(user) # No es necesario modificar el atributo lobby del usuario, se hace automáticamente

    @db_session
    def get_lobby_users(self, lobby_name: str) -> dict:
        lobby = Lobby.get(name=lobby_name)
        users_dict = [{'name': user.name} for user in lobby.users]
        users_dict.append({'host': lobby.host.name})
        return users_dict

''' Work in progress
class GameRepository:

    @db_session
    def create_Game(self, name: str, amount_players: int):
        Game(name=name, amount_players=amount_players)

    @db_session
    def get_all_cards_this_game(self, name: str):
        repo_card_Repository = CardRepository()
        Game.lobby.get(name=name).all_cards = repo_card_Repository.create_cards_for_this_game(name)

    @db_session
    def give_users(self, name: str) -> Set(User):
        repo_user = UserRepository()
        return repo_user.get_all_users()
'''