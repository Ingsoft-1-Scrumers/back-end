from pony.orm import *
from settings import DATABASE_FILENAME

db = Database()


class User(db.Entity):
    name = PrimaryKey(str)
    is_alive = Optional(bool)
    lobby = Optional('Lobby', reverse='users')
    hosting_lobby = Optional('Lobby', reverse='host')
    position = Optional('Position')
    hand = Set('Card')


class Lobby(db.Entity):
    name = PrimaryKey(str)
    password = Optional(str)
    min_players = Required(int, size=8)
    max_players = Required(int, size=8)
    users = Set(User, reverse='lobby')
    host = Required(User, reverse='hosting_lobby')
    game = Optional('Game')


class Position(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    game = Required('Game', reverse='positions')
    turn = Optional('Game', reverse='turn')


class Game(db.Entity):
    lobby = PrimaryKey(Lobby)
    amount_players = Required(int, size=8, unsigned=True)
    turn = Required(Position, reverse='turn')
    positions = Set(Position, reverse='game')
    all_cards = Set('Card', reverse='game_associated')
    deck_cards = Set('Card', reverse='game_deck')


class Card(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    type = Required(str)
    description = Required(str)
    game_associated = Required(Game, reverse='all_cards')
    game_deck = Optional(Game, reverse='deck_cards')
    user_hand = Optional(User)


db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)
db.generate_mapping(create_tables=True)
