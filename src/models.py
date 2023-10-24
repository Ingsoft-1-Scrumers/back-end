from pony.orm import *
from settings import DATABASE_FILENAME

db = Database()

class User(db.Entity):
    name = PrimaryKey(str)
    lobby = Optional('Lobby', reverse='users')
    hosting_lobby = Optional('Lobby', reverse='host')
    ready = Optional(bool, default=False)
    position = Optional('Position')
    hand = Set('Card')
    role = Optional(str, default="Humano")
    quarantine = Optional(int, default=0)

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
    initial_amount = Optional(int)
    all_cards = Set('Card', reverse='game_associated')
    deck_cards = Set('Card', reverse='game_deck')
    direction = Required(bool, default=True)
    status = Required(str, default='game_not_started')
    discard_or_play = Optional(str)
    defend_or_skip = Optional(str)
    defend_or_exchange = Optional(str)
    effect_to_be_applied = Optional(str)
    target_to_be_afflicted = Optional(str)
    exchange_card_user_start = Optional(int, default=0)
    exchange_card_user_finish = Optional(int, default=0)
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