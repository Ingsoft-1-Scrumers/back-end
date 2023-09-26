from models import Game, Card
from pony.orm import db_session
from template import *

class GameRepository:

    @db_session
    def create_card(self, card_template, game_associated : Game):    #recibe un dict
        Card(card_name = card_template["card_name"], 
            card_type = card_template["card_type"],
             description = card_template["description"],
             game_associated = game_associated)
    
    @db_session
    def create_game(self, name : str, amount_players : int):    #recibe un dict
        Game(name = name,
             amount_players = amount_players)
        
    @db_session
    def put_card_in_deck(self, card_to_put : Card, game_with_deck : Game):
        card_to_put.game_deck = game_with_deck

    @db_session
    def create_cards_for_this_game(self, this_game : Game):
        
        for template_name in all_templates: #para crear cartas de cada template
            
            #cuantas cartas de este template segun el numero de jugadores en la partida
            amount_cards_template = template_name['quantity_numb_players'][this_game.amount_players - 4]

            #creamos esa cantidad de cartas
            for card_number in range(amount_cards_template):
                self.create_card(template_name, this_game)
                
    @db_session
    def add_cards_to_deck(self, this_game : Game):
        
        for card_created in Card.select(game_associated = this_game):
            self.put_card_in_deck(card_created, this_game)
            
    """
    cartatirar = Card.select(id=11)
    repo.remove_card_from_deck(cartatirar.first())
    
    """
    @db_session
    def remove_card_from_deck(self, card_discard : Card):
        
        this_game = card_discard.game_associated
        this_game.deck.remove(card_discard)
        
    
        
        
            