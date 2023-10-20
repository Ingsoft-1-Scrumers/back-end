from pony.orm import *
from settings import DATABASE_FILENAME

db = Database()

class User(db.Entity):
    name = PrimaryKey(str)
    is_alive = Optional(bool, default=True)
    role = Optional(str, default="Humano")
    lobby = Optional('Lobby', reverse='users')
    hosting_lobby = Optional('Lobby', reverse='host')
    position = Optional('Position')
    hand = Set('Card')
    quarantine = Optional(bool, default=False)

class Lobby(db.Entity):
    name = PrimaryKey(str)
    min_players = Required(int, size=8)
    max_players = Required(int, size=8)
    password = Optional(str)
    users = Set(User, reverse='lobby')
    host = Required(User, reverse='hosting_lobby')
    game = Optional('Game', cascade_delete=True)
    
class Game(db.Entity):
    lobby = PrimaryKey(Lobby)
    name = Required(str)
    amount_players = Required(int, size=8, unsigned=True)
    turn = Optional('Position', reverse='turn')
    positions = Set('Position', reverse='game')
    all_cards = Set('Card', reverse='game_associated')
    deck_cards = Set('Card', reverse='game_deck')
    direction = Required(bool, default=True)
    status = Required(str, default='game_not_started')
    discard_or_play = Optional(str)
    effect_to_be_applied = Optional(str)
    user_target_effect = Optional(str)
    exchange_card_user_start = Optional(int)
    exchange_card_user_finish = Optional(int)
    exchange_user_start = Optional(str)
    exchange_user_finish = Optional(str)

class Position(db.Entity):
    user = PrimaryKey(User)
    number = Required(int)
    right_door = Required(bool, default=False)
    left_door = Required(bool, default=False)
    game = Required('Game', reverse='positions')
    turn = Optional('Game', reverse='turn')

class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    type = Required(str)
    game_associated = Required(Game, reverse='all_cards')
    game_deck = Optional(Game, reverse='deck_cards')
    user_hand = Optional(User)

db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)