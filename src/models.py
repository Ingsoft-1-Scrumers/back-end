from pony.orm import *

db = Database()

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    is_alive = Optional(bool)
    in_quarantine = Optional(bool)
    role_in_game = Optional(str)
    game_name = Optional(str)
    hand_cards = Optional(str)
    position_in_game = Optional(int)
    lobby_name = Optional(str)

class Game(db.Entity):
    amount_players = Required(int, size=8, unsigned=True)
    amount_infected = Optional(int, 0, size=8, unsigned=True)
    lobby = Required(Lobby)
    positions = Set(Position, reverse='game')
    turn = Required(Position, reverse='is_turn')


db.bind(provider='sqlite', filename='user_db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)