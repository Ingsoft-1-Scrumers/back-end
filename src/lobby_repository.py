from models import Lobby, User
from pony.orm import db_session

class LobbyRepository:

    @db_session
    def create_lobby(self, lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
        host = User.get(name=host_name) # Usar user_repo
        if (password == 'empty'):
            password = None
        lobby = Lobby(name=lobby_name, min_players=min_players, max_players=max_players, password=password, host=host)
        lobby.users.add(host)
        host.hosting_lobby = lobby # Usar user_repo

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
        user = User.get(name=user_name) # Usar user_repo
        lobby = Lobby.get(name=lobby_name)
        lobby.users.add(user)
        user.lobby = lobby # Usar user_repo

    @db_session
    def is_user_in_lobby(self, lobby_name: str, user_name: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        users_dict = [{'name': user.name} for user in lobby.users]
        result = False
        for user in users_dict:
            if user['name'] == user_name:
                result = True
        return result
    
    @db_session
    def is_user_host(self, lobby_name: str, user_name: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        return lobby.host.name == user_name

    @db_session
    def get_lobby_users(self, lobby_name: str) -> dict:
        lobby = Lobby.get(name=lobby_name)
        users_dict = [{'name': user.name} for user in lobby.users]
        users_dict.append({'host': lobby.host.name})
        return users_dict