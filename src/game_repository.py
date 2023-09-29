from models import Game, Card, User
from pony.orm import db_session
from template import *

CARDS_PER_USER = 4

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
    def create_user(self, name : str):    #recibe un dict
        User(name = name)    
        
    #---------------------------------------------------------------------------
    
    
    
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
        this_game.deck_cards.remove(card_discard)
    
    
    @db_session
    def random_card_from_deck(self, this_game : Game) -> Card:
        random_card = this_game.deck_cards.random(1)[0] #saco una carta del mazo
        self.remove_card_from_deck(random_card) #elimino la carta del mazo
        return random_card
    
    
    @db_session
    def random_card_from_deck_ingoring_panic(self, this_game : Game) -> Card:
        
        deck_without_panic = this_game.deck_cards.select(lambda card: card.card_type != "Panico")   #tipo Query
        
        random_card = deck_without_panic.random(1)[0] #saco una carta del mazo
        self.remove_card_from_deck(random_card) #elimino la carta del mazo
        return random_card


    @db_session
    def deal_4_cards_user(self, this_user : User, this_game : Game):
        
        for number_card in range(CARDS_PER_USER):
            random_card = self.random_card_from_deck_ingoring_panic(this_game)
            random_card.user_hand = this_user
            
            
    @db_session
    def deal_cards_all_users(self, this_game : Game):
        
        for actual_user in this_game.users:
            self.deal_4_cards_user(actual_user, this_game)
            
            
    @db_session
    def steal_card_from_deck(self, this_user : User):
        
        game_user = this_user.game_in
        random_card = self.random_card_from_deck(game_user)
        random_card.user_hand = this_user
        
        
    @db_session
    def discard_card_from_hand(self, this_user : User, card_discard : Card):
        
        hand_to_modify = this_user.hand
        hand_to_modify.remove(card_discard)

