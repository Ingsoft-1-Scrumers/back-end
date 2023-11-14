from models import *
from pony.orm import db_session

#! Convencion: Si ya tenemos un objeto, podemos acceder a sus atributos sin usar una clase repository

class UserRepository:

    @db_session
    def create_user(self, user_name: str):
        User(name=user_name)

    @db_session
    def remove_user(self, user_name: str):
        user = self.get_user(user_name)
        user.delete()

    @db_session
    def get_user(self, user_name: str) -> User:
        user = User.get(name=user_name)
        if user is None:
            raise ValueError(f"User does not exist with name: {user_name}")
        return user
    
    @db_session
    def is_user_ready(self, user_name: str) -> bool:
        user = self.get_user(user_name)
        return user.ready
    
    @db_session
    def set_user_ready(self, user_name: str, ready: bool):
        user = self.get_user(user_name)
        user.ready = ready

    @db_session
    def get_user_lobby(self, user_name: str) -> str:
        user = self.get_user(user_name)
        lobby = user.lobby
        return lobby.name
    
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
        hand_dict = sorted(hand_dict, key=lambda x: x.get('name', ''))
        return hand_dict

    @db_session
    def get_user_hand_int(self, user_name: str) -> [int]:
        hand = self.get_hand(user_name)
        result = []
        for card in hand:
            result.append(card.id)
        return result
    
    @db_session
    def get_user_cards(self, user_name: str) -> str:
        hand = self.get_hand(user_name)
        result = []
        for card in hand:
            result.append(card.name)
        result_string = ', '.join(map(str, result))
        return result_string

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
    def add_card_to_hand(self, user_name: str, card_id: int):
        card_repo = CardRepository()
        user = self.get_user(user_name)
        card = card_repo.get_card(card_id)
        card.user_hand = user
    
    @db_session
    def get_user_game(self, user_name: str) -> Game:
        lobby_repo = LobbyRepository()
        user = self.get_user(user_name)
        lobby = user.lobby
        if lobby is None:
            raise ValueError("User does not have a lobby")
        game = lobby_repo.get_game(lobby.name)
        return game

    @db_session
    def is_user_in_quarantine(self, user_name: str) -> bool:
        user = self.get_user(user_name)
        return (user.quarantine > 0)

    @db_session
    def set_user_in_quarantine_next_player(self, user_name: str):
        user = self.get_user(user_name)
        user.quarantine = 3

    @db_session
    def set_user_in_quarantine_previous_player(self, user_name: str):
        user = self.get_user(user_name)
        user.quarantine = 2

    @db_session
    def set_user_in_quarantine_false(self, user_name: str):
        user = self.get_user(user_name)
        user.quarantine = False

    @db_session
    def infect_effect(self, user_name: str):
        user = self.get_user(user_name)
        user.role = "Infectado"

    @db_session
    def user_death(self, user_name: str):
        position_repo = PositionRepository()
        user = self.get_user(user_name)
        user.lobby = None
        user.quarantine = 0
        position_repo.remove_position(user)
    
    @db_session
    def get_random_card_from_hand(self, user_name: str) -> Card:
        hand = self.get_hand(user_name)
        random_card = hand.random(1)[0]
        return random_card.id
    
    @db_session
    def get_position(self, user_name: str) -> Position:
        user = self.get_user(user_name)
        return user.position

    @db_session
    def decrease_quarantine(self, user_name: str):
        user = self.get_user(user_name)
        user.quarantine -= 1

    @db_session
    def get_role(self, user_name: str) -> str:
        user = self.get_user(user_name)
        return user.role

class LobbyRepository:

    @db_session
    def create_lobby(self, lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
        user_repo = UserRepository()
        host = user_repo.get_user(host_name)
        Lobby(name=lobby_name, min_players=min_players, max_players=max_players, password=password, host=host)
        self.add_user_to_lobby(lobby_name, host_name)

    @db_session
    def get_lobby(self, lobby_name: str) -> Lobby:
        lobby = Lobby.get(name=lobby_name)
        if lobby is None:
            raise ValueError(f"Lobby does not exist with name: {lobby_name}")
        return lobby
    
    @db_session
    def set_new_host(self, lobby_name: str, new_host: User):
        lobby = self.get_lobby(lobby_name)
        lobby.host = new_host

    @db_session
    def get_game(self, lobby_name: str) -> Game:
        lobby = self.get_lobby(lobby_name)
        game = lobby.game
        if game is None:
            raise ValueError(f"Game does not exist with name: {lobby_name}")
        return game
    
    @db_session
    def is_everyone_ready(self, lobby_name: str) -> bool:
        lobby_users = self.get_lobby_set_users(lobby_name)
        result = True
        for user in lobby_users:
            if not user.ready:
               result = False
               break
        return result
    
    @db_session
    def set_everyone_ready_false(self, lobby_name: str):
        lobby_users = self.get_lobby_set_users(lobby_name)
        for user in lobby_users:
            user.ready = False
            
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
        users_dict = sorted(users_dict, key=lambda x: x.get('name', ''))
        return users_dict
    
    @db_session 
    def get_lobby_users_no_host(self, lobby_name: str) -> [dict]:
        lobby_users = self.get_lobby_set_users(lobby_name)
        users_dict = [{'name': user.name} for user in lobby_users]
        users_dict = sorted(users_dict, key=lambda x: x.get('name', ''))
        return users_dict
    
    @db_session
    def get_joinable_lobby_listings(self) -> [dict]:
        not_started_lobbies = Lobby.select().where(game=None)
        joinable_lobbies = []
        for lobby in not_started_lobbies:
            if (len(lobby.users) != lobby.max_players):
                joinable_lobbies.append(lobby)
        joinable_lobbies_dict = [{'name': lobby.name,
                                  'total_players': len(lobby.users),
                                  'max_players': lobby.max_players,
                                  'secure': lobby.password is not None} for lobby in joinable_lobbies]
        joinable_lobbies_dict = sorted(joinable_lobbies_dict, key=lambda x: x.get('name', ''))
        return joinable_lobbies_dict
    
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
    def leave_lobby(self, lobby_name: str, user_name: str):
        user_repo = UserRepository()
        lobby_users = self.get_lobby_set_users(lobby_name)
        if user_repo.is_user_host(lobby_name, user_name):
            self.remove_all_users_from_lobby(lobby_name)
            self.remove_lobby(lobby_name)
        else:
            user = user_repo.get_user(user_name)
            lobby_users.remove(user)
    
    @db_session
    def remove_user_from_game(self, lobby_name: str, user_name: str):
        user_repo = UserRepository()
        lobby_users = self.get_lobby_set_users(lobby_name)

        if user_repo.is_user_host(lobby_name, user_name):
            user = user_repo.get_user(user_name)
            new_host = select([lobby_users]).where(lobby_users.c.name != user_name).first()
            self.set_new_host(lobby_name, new_host)
            lobby_users.remove(user)
        else:
            user = user_repo.get_user(user_name)
            lobby_users.remove(user)

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
    def is_lobby_private(self, lobby_name: str) -> bool:
        lobby_password = self.get_password(lobby_name)
        return lobby_password != "empty"

    @db_session
    def add_user_to_lobby(self, lobby_name: str, user_name: str):
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        lobby_users = self.get_lobby_set_users(lobby_name)
        lobby_users.add(user)

    @db_session
    def change_host(self, lobby_name: str, user_name: str):
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        lobby = self.get_lobby(lobby_name)
        lobby.host = user

    @db_session
    def remove_all_users_from_lobby(self, lobby_name: str):
        lobby_users = self.get_lobby_set_users(lobby_name)
        for user in lobby_users:
            user.lobby = None
            user.role = None
            user.hand = None
            user.hosting_lobby = None
            user.ready = False

    @db_session
    def remove_lobby(self, lobby_name: str):
        lobby = self.get_lobby(lobby_name)
        lobby.delete()


class GameRepository:

    @db_session
    def create_game(self, lobby_name: str, amount_players: int):
        lobby_repo = LobbyRepository()
        lobby = lobby_repo.get_lobby(lobby_name)
        Game(lobby=lobby, name=lobby_name, amount_players=amount_players, initial_amount=amount_players)

    @db_session
    def get_game(self, game_name: str) -> Game:
        game = Game.get(name=game_name)
        if game is None:
            raise ValueError(f"Game does not exist with name: {game_name}")
        return game 

    @db_session
    def get_game_status(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.status

    @db_session
    def set_game_status(self, game_name: str, status: str):
        game = self.get_game(game_name)
        game.status = status

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
    def get_turn_user(self, game_name: str) -> str:
        turn = self.get_turn(game_name)
        return turn.user.name
    
    @db_session
    def get_amount_players(self, game_name: str) -> int:
        game = self.get_game(game_name)
        return game.amount_players

    @db_session
    def set_initial_amount(self, game_name: str, initial_amount_players: int):
        game = self.get_game(game_name)
        game.initial_amount = initial_amount_players

    @db_session
    def get_initial_amount(self, game_name: str):
        game = self.get_game(game_name)
        return game.initial_amount

    @db_session
    def get_n_position(self, n: int, game_name: str) -> Position:
        game_positions = self.get_all_positions(game_name) 
        n_position = game_positions.select().where(number=n).first() # Query
        return n_position

    @db_session
    def get_users_position(self, game_name: str) -> [dict]:
        positions = self.get_all_positions(game_name)
        users_dict = [{'name': position.user.name, 
                       'position': position.number, 
                       'left_door': position.left_door,
                       'quarantine': position.user.quarantine} for position in positions]
        users_dict = sorted(users_dict, key=lambda x: x.get('position', ''))
        return users_dict
    
    @db_session
    def assign_turn(self, position: Position, game_name: str):
        game = self.get_game(game_name)
        game.turn = position

    @db_session
    def remove_game(self, game_name: str):
        game = self.get_game(game_name)
        game.delete()

    @db_session
    def is_there_exchange_offer(self, lobby_name: str) -> bool:
        game = self.get_game(lobby_name)
        return game.exchange_card_user_start != 0

    @db_session
    def get_exchange_card_user_start(self, game_name: str) -> int:
        game = self.get_game(game_name)
        return game.exchange_card_user_start

    @db_session
    def get_exchange_card_user_finish(self, game_name: str) -> int:
        game = self.get_game(game_name)
        return game.exchange_card_user_finish

    @db_session
    def get_exchange_user_start(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.exchange_user_start

    @db_session
    def get_exchange_user_finish(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.exchange_user_finish

    @db_session
    def set_exchange_card_start(self, game_name: str, card_id: int):
        game = self.get_game(game_name)
        game.exchange_card_user_start = card_id

    @db_session
    def set_exchange_card_finish(self, game_name: str, card_id: int):
        game = self.get_game(game_name)
        game.exchange_card_user_finish = card_id

    @db_session
    def set_exchange_user_start(self, game_name: str, user_name: str):
        game = self.get_game(game_name)
        game.exchange_user_start = user_name

    @db_session
    def set_exchange_user_finish(self, game_name: str, user_name: str):
        game = self.get_game(game_name)
        game.exchange_user_finish = user_name

    @db_session
    def clean_exchange_data(self, game_name: str):
        game = self.get_game(game_name)
        game.exchange_user_start = "None"
        game.exchange_user_finish = "None"
        game.exchange_card_user_start = 0
        game.exchange_card_user_finish = 0

    @db_session
    def get_direction(self, game_name: str) -> bool:
        game = self.get_game(game_name)
        return game.direction

    @db_session
    def set_direction(self, game_name: str, new_direction: bool):
        game = self.get_game(game_name)
        game.direction = new_direction

    @db_session
    def set_discard_or_play(self, game_name: str, decision: str):
        game = self.get_game(game_name)
        game.discard_or_play = decision

    @db_session
    def get_discard_or_play(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.discard_or_play

    @db_session
    def set_effect_to_be_applied(self, game_name: str, effect: str):
        game = self.get_game(game_name)
        game.effect_to_be_applied = effect

    @db_session
    def get_effect_to_be_applied(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.effect_to_be_applied
    
    @db_session
    def set_target_to_be_afflicted(self, game_name: str, target: str):
        game = self.get_game(game_name)
        game.target_to_be_afflicted = target

    @db_session
    def get_target_to_be_afflicted(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.target_to_be_afflicted

    @db_session
    def set_defend_or_skip(self, game_name: str, decision: str):
        game = self.get_game(game_name)
        game.defend_or_skip = decision

    @db_session
    def get_defend_or_skip(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.defend_or_skip

    @db_session
    def set_defend_or_exchange(self, game_name: str, decision: str):
        game = self.get_game(game_name)
        game.defend_or_exchange = decision

    @db_session
    def get_defend_or_exchange(self, game_name: str) -> str:
        game = self.get_game(game_name)
        return game.defend_or_exchange

    @db_session
    def set_is_panic_card(self, game_name: str, boolean: bool):
        game = self.get_game(game_name)
        game.is_panic_card = boolean

    @db_session
    def get_is_panic_card(self, game_name: str) -> bool:
        game = self.get_game(game_name)
        return game.is_panic_card
    
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
    
    @db_session
    def get_card_dict(self, card_id: int) -> dict:
        card = self.get_card(card_id)
        card_dict = {'id': card.id,
                     'name': card.name, 
                     'type': card.type}
        return card_dict
    
    @db_session
    def get_card_name(self, card_id: int) -> str:
        card = self.get_card(card_id)
        return card.name
    
    @db_session
    def is_panic_card(self, card_id: int) -> bool:
        card = self.get_card(card_id)
        return card.type == "Panico"

class PositionRepository:

    @db_session
    def create_position(self, user: User, number: int, game: Game):
        Position(user=user, number=number, game=game)

    @db_session
    def get_number(self, position: Position) -> int:
        return position.number

    @db_session
    def set_position(self, position: Position, number: int):
        position.number = number

    @db_session
    def get_user(self, position: Position) -> User:
        return position.user
    
    @db_session
    def get_position(self, player: User) -> Position:
        position = Position.get(user=player)
        if position is None:
            raise ValueError("Position does not exist")
        return position
    
    @db_session
    def remove_position(self, user: User):
        position = self.get_position_user_name(user.name)
        position.delete()

    @db_session
    def get_right_door(self, position: Position) -> bool:
        return position.right_door
    
    @db_session
    def get_left_door(self, position: Position) -> bool:
        return position.left_door

    @db_session
    def set_right_door(self, position: Position, right_door: bool):
        position.right_door = right_door

    @db_session
    def set_left_door(self, position: Position, left_door: bool):
        position.left_door = left_door

    @db_session
    def get_numb_position(self, user_name: str) -> int:
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        pos = self.get_position(user)
        return pos.number

    @db_session
    def get_position_user_name(self, user_name: str) -> Position:
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        pos = self.get_position(user)
        return pos

    @db_session
    def get_user_name_position(self, position: Position) -> User:
        return position.user.name