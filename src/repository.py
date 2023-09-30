from models import *
from pony.orm import db_session
from settings import CARDS_PER_USER
from template import ALL_TEMPLATES

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

class CardRepository:

    @db_session
    def create_card(self, card_template, game_associated : Game):
        Card(name = card_template["card_name"], 
            type = card_template["card_type"],
             description = card_template["description"],
             game_associated = game_associated)

    @db_session
    def put_card_in_deck(self, card_to_put : Card, game_with_deck : Game):
        card_to_put.game_deck = game_with_deck

    @db_session
    def create_cards_for_this_game(self, this_game : Game):
        for template_name in ALL_TEMPLATES: 
            amount_cards_template = template_name['quantity_numb_players'][this_game.amount_players - 4]
            for card_number in range(amount_cards_template):
                self.create_card(template_name, this_game)
                
    @db_session
    def add_cards_to_deck(self, this_game : Game):
        for card_created in Card.select(game_associated = this_game):
            self.put_card_in_deck(card_created, this_game)
            
    @db_session
    def create_deck(self, this_game : Game):
        self.create_cards_for_this_game(this_game)
        self.add_cards_to_deck(this_game)
            
    @db_session
    def remove_card_from_deck(self, card_discard : Card):
        this_game = card_discard.game_associated
        this_game.deck_cards.remove(card_discard)
    
    @db_session
    def random_card_from_deck(self, this_game : Game) -> Card:
        random_card = this_game.deck_cards.random(1)[0] #saco una carta del mazo
        self.remove_card_from_deck(random_card) #elimino la carta del mazo
        return random_card
    
    @db_session
    def random_card_from_deck_ingoring_panic(self, this_game : Game) -> Card:
        deck_without_panic = this_game.deck_cards.select(lambda card: card.type != "Panico")   #tipo Query
        random_card = deck_without_panic.random(1)[0] #saco una carta del mazo
        self.remove_card_from_deck(random_card) #elimino la carta del mazo
        return random_card

    @db_session #UserRepository
    def deal_4_cards_user(self, this_user : User, this_game : Game):
        for number_card in range(CARDS_PER_USER):
            random_card = self.random_card_from_deck_ingoring_panic(this_game)
            random_card.user_hand = this_user
            
    @db_session
    def deal_cards_all_users(self, this_game : Game):
        for actual_user in this_game.users:
            self.deal_4_cards_user(actual_user, this_game)
            
    @db_session
    def steal_card_from_deck(self, this_user : User) -> dict:
        game_user = this_user.game_in
        random_card = self.random_card_from_deck(game_user)
        random_card.user_hand = this_user
        card_dict = {'name': random_card.name, 
                      'type': random_card.type, 
                      'description': random_card.description}
        return card_dict
        
    @db_session #UserRepository
    def discard_card_from_hand(self, this_user : User, card_discard : Card):
        hand_to_modify = this_user.hand
        hand_to_modify.remove(card_discard)

    @db_session #UserRepository
    def get_user_hand(self, user_name: str) -> dict:
        user = User.select(name=user_name)
        hand_dict = [{'name': card.name, 
                      'type': card.type, 
                      'description': card.description} for card in user.first().hand]
        return hand_dict
    
    @db_session
    def recreate_empty_deck(self, this_game : Game):
        new_deck = this_game.all_cards.select(lambda card: card.user_hand == None)
        for card in new_deck:
            card.game_deck = this_game

class PositionRepository:

    @db_session
    def create_position(self, user: User, game: Game, turn):
        Position(user=user, game=game, turn=turn)

    @db_session
    def get_position(user: User) -> dict:
        position = Position.get(user=user)
        if position is None:
            raise ValueError("Position does not exist")
        return {'username': user.name, 'position': position.id}