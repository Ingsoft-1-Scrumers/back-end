from models import Lobby, User
from pony.orm import db_session

# TODO: Revisar si tenemos que usar UserRepository para obtener el usuario

class LobbyRepository:

    @db_session
    def create_lobby(self, lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
        host = User.get(name=host_name)
        lobby = Lobby(name=lobby_name, min_players=min_players, max_players=max_players, password=password, host=host)
        lobby.users.add(host)
        # TODO: Hay que encriptar la password?

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
        return lobby.password == password

    @db_session
    def add_user_to_lobby(self, lobby_name: str, user_name : str):
        user = User.get(name=user_name)
        lobby = Lobby.get(name=lobby_name)
        lobby.users.add(user)

    @db_session
    def is_user_in_lobby(self, lobby_name: str, user_name: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        return user_name in lobby.users
    
    @db_session
    def is_user_host(self, lobby_name: str, user_name: str) -> bool:
        lobby = Lobby.get(name=lobby_name)
        return lobby.host.name == user_name

    @db_session
    def get_lobby_users(self, lobby_name: str) -> dict:
        lobby = Lobby.get(name=lobby_name)
        users = lobby.users
        return users # Checkear si esto devuelve un diccionario o un objeto