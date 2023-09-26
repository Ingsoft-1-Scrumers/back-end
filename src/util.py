from game_repository import GameRepository
from models import Game, Card
from template import *
from pony.orm import db_session

class deckrepository:
    
    def __init__(
        self, game_repo: GameRepository,
        this_game: Game,
    ):
        self.game_repo = game_repo
        self.this_game = this_game
    
    @db_session #sin esto no anda :(
    def create_deck(self):
        self.game_repo.create_cards_for_this_game(self.this_game)
        self.game_repo.add_cards_to_deck(self.this_game)
        
                
    