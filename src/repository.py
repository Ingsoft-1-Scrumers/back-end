from models import *
from pony.orm import db_session
from settings import CARDS_PER_USER
from template import ALL_TEMPLATES

#! Convencion: Si ya tenemos un objeto, podemos acceder a sus atributos sin usar una clase repository

class UserRepository:

    @db_session
    def create_user(self, user_name: str):
        User(name=user_name)

    @db_session
    def get_user(self, user_name: str) -> User:
        user = User.get(name=user_name)
        if user is None:
            raise ValueError("User does not exist with name: {}".format(user_name))
        return user
    
    @db_session
    def get_hand(self, user_name: str) -> Set(Card):
        user = self.get_user(user_name)
        hand = user.hand
        if hand is None:
            raise ValueError("User does not have a hand")
        return hand

    @db_session
    def get_user_hand(self, user_name: str) -> [dict]:
        hand = self.get_hand(user_name)
        hand_dict = [{'id': card.id,
                    'name': card.name, 
                    'type': card.type} for card in hand]
        return hand_dict

    @db_session
    def get_total_cards(self, user_name: str) -> int:
        hand = self.get_hand(user_name)
        return len(hand)

    @db_session
    def user_exists(self, user_name: str) -> bool:
        return User.exists(name=user_name)
    
    @db_session
    def is_user_in_a_lobby(self, user_name: str) -> bool:
        user = self.get_user(user_name)
        return user.lobby is not None
    
    @db_session
    def is_target_in_a_lobby(self, target_user_name: str) -> bool:
        target = self.get_user(target_user_name)
        return target.lobby is not None

    @db_session 
    def is_user_in_lobby(self, lobby_name: str, user_name: str) -> bool:
        lobby_repo = LobbyRepository()
        lobby_users = lobby_repo.get_lobby_set_users(lobby_name)
        return lobby_users.select().where(name=user_name).exists()
    
    @db_session 
    def is_target_in_lobby(self, lobby_name: str, target_user_name: str) -> bool:
        lobby_repo = LobbyRepository()
        lobby_users = lobby_repo.get_lobby_set_users(lobby_name)
        return lobby_users.select().where(name=target_user_name).exists()
    
    @db_session
    def is_user_alive(self, user_name: str) -> bool:
        user = self.get_user(user_name)
        return user.is_alive
    
    @db_session
    def is_target_alive(self, target_user_name: str) -> bool:
        target = self.get_user(target_user_name)
        return target.is_alive
    
    @db_session
    def is_user_host(self, lobby_name: str, user_name: str) -> bool:
        lobby_repo = LobbyRepository()
        host_name = lobby_repo.get_host_name(lobby_name)
        return host_name == user_name

    @db_session
    def is_user_turn(self, lobby_name: str, user_name: str) -> bool:
        game_repo = GameRepository()
        game_turn_position = game_repo.get_turn(lobby_name)
        user_turn = game_turn_position.user
        return user_turn.name == user_name

    @db_session
    def check_user_has_card(self, user_name: str, card_id: int) -> bool:
        hand = self.get_hand(user_name)
        result = False
        for card in hand:
            if card.id == card_id:
                result = True
                break
        return result
    
    @db_session
    def get_user_game(self, user_name: str) -> Game:
        lobby_repo = LobbyRepository()
        user = self.get_user(user_name)
        lobby = user.lobby
        if lobby is None:
            raise ValueError("User does not have a lobby")
        game = lobby_repo.get_game(lobby.name)
        return game

class LobbyRepository:

    @db_session #! No hay lobbies sin contraseña
    def create_lobby(self, lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
        user_repo = UserRepository()
        host = user_repo.get_user(host_name)
        Lobby(name=lobby_name, min_players=min_players, max_players=max_players, password=password, host=host)
        self.add_user_to_lobby(lobby_name, host_name)

    @db_session
    def get_lobby(self, lobby_name: str) -> Lobby:
        lobby = Lobby.get(name=lobby_name)
        if lobby is None:
            raise ValueError("Lobby does not exist with name: {}".format(lobby_name))
        return lobby
    
    @db_session
    def get_game(self, lobby_name: str) -> Game:
        lobby = self.get_lobby(lobby_name)
        game = lobby.game
        if game is None:
            raise ValueError("Game does not exist with name: {}".format(lobby_name))
        return game
    
    @db_session
    def get_lobby_set_users(self, lobby_name: str) -> Set(User):
        lobby = self.get_lobby(lobby_name)
        return lobby.users

    @db_session
    def get_min_players(self, lobby_name: str) -> int:
        lobby = self.get_lobby(lobby_name)
        return lobby.min_players
    
    @db_session
    def get_max_players(self, lobby_name: str) -> int:
        lobby = self.get_lobby(lobby_name)
        return lobby.max_players

    @db_session
    def get_password(self, lobby_name: str) -> str:
        lobby = self.get_lobby(lobby_name)
        return lobby.password

    @db_session
    def get_host_name(self, lobby_name: str) -> str:
        lobby = self.get_lobby(lobby_name)
        return lobby.host.name

    @db_session
    def get_amount_users(self, lobby_name: str) -> int:
        lobby = self.get_lobby(lobby_name)
        return len(lobby.users)

    @db_session 
    def get_lobby_users(self, lobby_name: str) -> [dict]:
        lobby_users = self.get_lobby_set_users(lobby_name)
        users_dict = [{'name': user.name} for user in lobby_users]
        users_dict.append({'host': self.get_host_name(lobby_name)})
        return users_dict
    
    @db_session
    def is_game_started(self, lobby_name: str) -> bool:
        lobby = self.get_lobby(lobby_name)
        return lobby.game is not None

    @db_session 
    def lobby_exists(self, lobby_name: str) -> bool:
        return Lobby.exists(name=lobby_name)
    
    @db_session
    def is_lobby_full(self, lobby_name: str) -> bool:
        max_players = self.get_max_players(lobby_name)
        lobby_users = self.get_lobby_set_users(lobby_name)
        return len(lobby_users) == max_players
    
    @db_session
    def can_start_game(self, lobby_name: str) -> bool:
        min_players = self.get_min_players(lobby_name)
        lobby_users = self.get_lobby_set_users(lobby_name)
        return len(lobby_users) >= min_players
    
    @db_session
    def is_password_correct(self, lobby_name: str, password: str) -> bool:
        lobby_password = self.get_password(lobby_name)
        return lobby_password == password

    @db_session
    def add_user_to_lobby(self, lobby_name: str, user_name: str):
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        lobby_users = self.get_lobby_set_users(lobby_name)
        lobby_users.add(user)

    @db_session
    def remove_all_users_from_lobby(self, lobby_name: str):
        lobby_users = self.get_lobby_set_users(lobby_name)
        for user in lobby_users:
            user.lobby = None

    @db_session
    def remove_lobby(self, lobby_name: str):
        lobby = self.get_lobby(lobby_name)
        lobby.delete()

    @db_session
    def get_lobbies(self) -> dict: #Ver type del return
        lobbies = Lobby.select()
        lobbies_dict = [{'name': lobby.name, 
                        'min_players': lobby.min_players,
                        'max_players': lobby.max_players,
                        'amount_users': len(lobby.users)} for lobby in lobbies]
        return lobbies_dict 

class GameRepository:

    @db_session
    def create_game(self, lobby_name: str, amount_players: int):
        lobby_repo = LobbyRepository()
        lobby = lobby_repo.get_lobby(lobby_name)
        Game(lobby=lobby, name=lobby_name, amount_players=amount_players)

    @db_session
    def get_game(self, game_name: str) -> Game:
        game = Game.get(name=game_name)
        if game is None:
            raise ValueError("Game does not exist with name: {}".format(game_name))
        return game 

    @db_session
    def get_all_cards(self, game_name: str) -> Set(Card):
        game = self.get_game(game_name)
        return game.all_cards

    @db_session
    def get_all_positions(self, game_name: str) -> Set(Position):
        game = self.get_game(game_name)
        return game.positions
    
    @db_session
    def get_turn(self, game_name: str) -> Position:
        game = self.get_game(game_name)
        return game.turn
    
    @db_session
    def get_amount_players(self, game_name: str) -> int:
        game = self.get_game(game_name)
        return game.amount_players
    
    @db_session
    def get_n_position(self, n: int, game_name: str) -> Position:
        game_positions = self.get_all_positions(game_name) 
        n_position = game_positions.select().where(number=n).first() # Query
        return n_position

    @db_session
    def get_users_position(self, game_name: str) -> [dict]:
        positions = self.get_all_positions(game_name)
        users_dict = [{'name': position.user.name, 'position': position.number} for position in positions]
        return users_dict
    
    @db_session
    def assign_turn(self, position: Position, game_name: str):
        game = self.get_game(game_name)
        game.turn = position

    @db_session
    def remove_game(self, game_name: str):
        game = self.get_game(game_name)
        game.delete()
    
class CardRepository:

    @db_session
    def create_card(self, card_template, game : Game):
        Card(name = card_template["card_name"], 
            type = card_template["card_type"],
            game_associated = game)

    @db_session
    def get_card(self, card_id: int) -> Card:
        card = Card.get(id=card_id)
        if card is None:
            raise ValueError("Card does not exist")
        return card

class PositionRepository:

    @db_session
    def create_position(self, user: User, number: int, game: Game):
        Position(user=user, number=number, game=game)