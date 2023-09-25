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
    lobby_name = Optional(str)
    position = Optional('Position')


class Position(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    obstacle = Optional(str)

db.bind(provider='sqlite', filename='user_db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)