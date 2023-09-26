from pony.orm import (Database, Required, Set, Optional)

db = Database()

class Game(db.Entity):
    name = Required(str)
    amount_players = Required(int)
    all_cards = Set('Card', reverse = 'game_associated')
    deck = Set('Card', reverse = 'game_deck')  # One-to-many relationship: one game can have many cards in the deck
    
class Card(db.Entity):
    card_name = Required(str)
    card_type = Required(str)
    description = Required(str)
    game_associated = Required(Game, reverse='all_cards')
    game_deck = Optional(Game, reverse='deck')
    #user = Optional(User)

db.bind(provider='sqlite', filename='user_db.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

"""
from game_repository import GameRepository
repo = GameRepository()
repo.create_game("lucia game", 4)
from models import Game
Game.select().show()
from models import Card
Card.select().show()
from util import deckrepository
drepo = deckrepository(repo, Game[1])

drepo.create_deck()
"""