from repository import *
from settings import CARDS_PER_USER
from template import ALL_TEMPLATES

class GameLogic:

    @db_session
    def start_game(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        game_repo = GameRepository()

        user_amount = lobby_repo.get_amount_users(lobby_name)
        game_repo.create_game(lobby_name, user_amount)
        game = lobby_repo.get_game(lobby_name)
        users = lobby_repo.get_lobby_set_users(lobby_name)
        
        self.create_deck(game)
        self.deal_cards_all_users(users, game)
        self.assign_positions(users, game)
        self.assign_turn(lobby_name, 1) 

    @db_session
    def create_deck(self, game : Game):
        self.create_cards_for_game(game)
        self.add_cards_to_deck(game)

    @db_session
    def create_cards_for_game(self, game : Game):
        card_repo = CardRepository()
        for template_name in ALL_TEMPLATES: 
            amount_cards_template = template_name['quantity_numb_players'][game.amount_players - 4]
            for cards in range(amount_cards_template):
                card_repo.create_card(template_name, game)

    @db_session
    def add_cards_to_deck(self, game : Game):
        for card_created in game.all_cards:
            card_created.game_deck = game
            
    @db_session
    def assign_the_thing(self, users : Set(User), game : Game):
        the_thing_user = users.random(1)[0] #agarro user random
        the_thing_user.role = "The thing"   #ahora es la cosa
        the_thing_card = game.deck_cards.select(lambda card: card.name == "La cosa").first()    #buscamos la carta de la cosa en el mazo
        the_thing_card.user_hand = the_thing_user   #le damos esa carta al user q es la cosa
        self.remove_card_from_deck(the_thing_card)  #sacamos la carta de la cosa del mazo
        

    @db_session
    def deal_cards_all_users(self, users : Set(User), game : Game):
        self.assign_the_thing(users, game)
        for user in users:
            if user.role == "The thing":
                num_cards_to_deal = CARDS_PER_USER-1
            else:
                num_cards_to_deal = CARDS_PER_USER
            for number_card in range(num_cards_to_deal):
                random_card = self.random_card_from_deck_without_panic_infection(game)
                random_card.user_hand = user

    @db_session
    def random_card_from_deck_ingoring_panic(self, game : Game) -> Card:
        deck_without_panic = game.deck_cards.select(lambda card: card.type != "Panico")
        random_card = deck_without_panic.random(1)[0] 
        self.remove_card_from_deck(random_card)
        return random_card
    
    @db_session
    def random_card_from_deck_without_panic_infection(self, game : Game) -> Card:
        deck_to_deal = game.deck_cards.select(lambda card: card.type != "Panico"
                                                            and card.type != "Contagio")
        random_card = deck_to_deal.random(1)[0] 
        self.remove_card_from_deck(random_card)
        return random_card

    @db_session
    def random_card_from_deck(self, game : Game) -> Card:
        random_card = game.deck_cards.random(1)[0]
        self.remove_card_from_deck(random_card)
        return random_card

    @db_session
    def remove_card_from_deck(self, card_discard : Card):
        game = card_discard.game_associated
        game.deck_cards.remove(card_discard)

    @db_session
    def assign_positions(self, users: Set(User), game: Game):
        position_repo = PositionRepository()
        num_order = 1
        for user in users:
            position_repo.create_position(user, num_order, game)
            num_order += 1

    @db_session
    def assign_turn(self, lobby_name: str, num: int):
        game_repo = GameRepository()
        pos_n = game_repo.get_n_position(num, lobby_name)
        game_repo.assign_turn(pos_n, lobby_name)

    @db_session
    def is_empty_deck(self, game: Game) -> bool:
        return len(game.deck_cards)==0

    @db_session
    def steal_card_from_deck(self, user_name: str) -> dict:
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        game = user_repo.get_user_game(user_name)
        if self.is_empty_deck(game):
            self.recreate_empty_deck(game)
        random_card = self.random_card_from_deck(game)
        random_card.user_hand = user
        card_dict = {'id': random_card.id,
                     'name': random_card.name, 
                     'type': random_card.type}
        return card_dict  

    @db_session
    def recreate_empty_deck(self, game : Game):
        new_deck = game.all_cards.select(lambda card: card.user_hand == None) 
        for card in new_deck:
            card.game_deck = game

    @db_session
    def play_card(self, user_name: str, id_card: int, lobby_name: str):
        user_repo = UserRepository()
        user = user_repo.get_user(user_name)
        self.discard_card_from_hand(user, id_card)
        self.next_turn(lobby_name)

    @db_session 
    def discard_card_from_hand(self, user: User, id_card: int):
        card_repo = CardRepository()
        card_discard = card_repo.get_card(id_card)
        hand_to_modify = user.hand
        hand_to_modify.remove(card_discard)

    @db_session
    def next_turn(self, lobby_name: str):
        game_repo = GameRepository()
        game = game_repo.get_game(lobby_name)
        amount_players = game_repo.get_amount_players(lobby_name)
        actual_turn = game_repo.get_turn(lobby_name)
        position_number = actual_turn.number

        if(position_number != amount_players):
            new_turn_position = game_repo.get_n_position(position_number+1, lobby_name)
        else:
            new_turn_position = game_repo.get_n_position(1, lobby_name)
        
        game.turn = new_turn_position

    @db_session
    def validate_swap_card(self, user_name: str, id_card: int, target_user_name: str) -> bool:
        valid_result = True
        user_repo = UserRepository()
        card_repo = CardRepository()
        user = user_repo.get_user(user_name)
        target_user = user_repo.get_user(target_user_name)
        card_to_swap = card_repo.get_card(id_card)
        
        if (card_to_swap.type == "Panico" or card_to_swap.name == "La cosa"):
            valid_result = False
        elif (card_to_swap.name == "Infectado"):
            num_infect = len(user.hand.select(lambda card : card.name == "Infectado"))
            if (user.role == "Human"):
                valid_result = False
            elif (user.role == "Infectado" and num_infect == 1):
                valid_result = False
            elif (user.role == "Infectado" and target_user.role != "The thing"):
                valid_result = False
            else:
                pass
        else: #otras cartas normies
            pass
        
        return valid_result
        
    #no se puede descartar la cosa, y si estas infectado si o si te tenes q quedar con 1
    @db_session
    def only_discard_card(self, user_name: str, id_card: int, lobby_name: str):
        user_repo = UserRepository()
        card_repo = CardRepository()
        user = user_repo.get_user(user_name)
        
        card_to_discard = card_repo.get_card(id_card)
        if(card_to_discard.name == "La cosa"):
            raise ValueError("You cannot discard this card")
        elif (card_to_discard.name == "Infectado"):
            num_infect = len(user.hand.select(lambda card : card.name == "Infectado"))
            if(user.role == "Infected" and num_infect == 1):
                raise ValueError("You cannot discard this card")
        self.discard_card_from_hand(user, id_card)
        self.next_turn(lobby_name)

    @db_session
    def end_game(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        game_repo = GameRepository()
        game_repo.remove_game(lobby_name)
        lobby_repo.remove_all_users_from_lobby(lobby_name)
        lobby_repo.remove_lobby(lobby_name)