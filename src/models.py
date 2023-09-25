from pony.orm import *

db = Database()

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    is_alive = Optional(bool)
    in_quarantine = Optional(bool)
    role_in_game = Optional(str)
    lobby = Optional('Lobby', reverse='users')
    hosting_lobby = Optional('Lobby', reverse='host')

class Lobby(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    min_players = Required(int, size=8)
    max_players = Required(int, size=8)
    password = Optional(str)
    users = Set(User, reverse='lobby')
    host = Required(User, reverse='hosting_lobby')

db.bind(provider='sqlite', filename='la_cosa_db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)