from repository import *
from settings import CARDS_PER_USER
from template import ALL_TEMPLATES

class GameLogic:

    def __init__(self):
        self.user_repo = UserRepository()
        self.lobby_repo = LobbyRepository()
        self.game_repo = GameRepository()
        self.card_repo = CardRepository()
        self.position_repo = PositionRepository()

    @db_session
    def start_game(self, lobby_name: str):
        user_amount = self.lobby_repo.get_amount_users(lobby_name)
        self.game_repo.create_game(lobby_name, user_amount)
        game = self.lobby_repo.get_game(lobby_name)
        users = self.lobby_repo.get_lobby_set_users(lobby_name)
        
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
        for template_name in ALL_TEMPLATES: 
            amount_cards_template = template_name['quantity_numb_players'][game.amount_players - 4]
            for cards in range(amount_cards_template):
                self.card_repo.create_card(template_name, game)

    @db_session
    def add_cards_to_deck(self, game : Game):
        for card_created in game.all_cards:
            card_created.game_deck = game
            
    @db_session
    def assign_the_thing(self, users : Set(User), game : Game):
        the_thing_user = users.random(1)[0]
        the_thing_user.role = "Cosa"
        the_thing_card = game.deck_cards.select(lambda card: card.name == "Cosa").first()
        the_thing_card.user_hand = the_thing_user
        self.remove_card_from_deck(the_thing_card)

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
        deck_to_deal = game.deck_cards.select(lambda card: card.type != "Panico" and card.type != "Contagio")
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
        num_order = 1
        for user in users:
            self.position_repo.create_position(user, num_order, game)
            num_order += 1

    @db_session
    def assign_turn(self, lobby_name: str, num: int):
        pos_n = self.game_repo.get_n_position(num, lobby_name)
        self.game_repo.assign_turn(pos_n, lobby_name)

    @db_session
    def is_empty_deck(self, game: Game) -> bool:
        return len(game.deck_cards)==0

    @db_session
    def steal_card_from_deck(self, user_name: str) -> dict:
        user = self.user_repo.get_user(user_name)
        game = self.user_repo.get_user_game(user_name)
        
        if self.is_empty_deck(game):
            self.recreate_empty_deck(game)
            
        random_card = self.random_card_from_deck(game)
        random_card.user_hand = user
        card_dict = {'id': random_card.id,
                     'name': random_card.name, 
                     'type': random_card.type}
        return card_dict  

    @db_session 
    def steal_card_from_deck_no_panic(self, user_name: str) -> dict:
        user = self.user_repo.get_user(user_name)
        game = self.user_repo.get_user_game(user_name)
        
        if self.is_empty_deck(game):
            self.recreate_empty_deck(game)
            
        random_card = self.random_card_from_deck_ingoring_panic(game)
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
    def discard_card_from_hand(self, user: User, id_card: int):
        card_discard = self.card_repo.get_card(id_card)
        hand_to_modify = user.hand
        hand_to_modify.remove(card_discard)

    @db_session
    def discard_card(self, user_name: str, id_card: int):
        user = self.user_repo.get_user(user_name)
        self.discard_card_from_hand(user, id_card)

    @db_session
    def next_turn(self, lobby_name: str, direction: bool):
        amount_players = self.game_repo.get_amount_players(lobby_name)
        actual_turn = self.game_repo.get_turn(lobby_name)
        position_number = actual_turn.number

        new_turn_position = None
        while new_turn_position == None:
            if direction: # True = Sentido horario
                new_turn_position = self.game_repo.get_n_position((position_number % amount_players) + 1, lobby_name)

                if (new_turn_position == None):
                    position_number = (position_number % amount_players) + 1
                    
            else: # False = Sentido antihorario
                if position_number == 1:
                    new_turn_position = self.game_repo.get_n_position(amount_players, lobby_name)
                    if (new_turn_position == None):
                        position_number = amount_players
                else:
                    new_turn_position = self.game_repo.get_n_position(position_number-1, lobby_name)
                    if (new_turn_position == None):
                        position_number -= 1

        self.assign_turn(lobby_name, new_turn_position.number)

    @db_session
    def validate_swap_card(self, user_name: str, id_card: int, target_user_name: str) -> bool:
        user = self.user_repo.get_user(user_name)
        target_user = self.user_repo.get_user(target_user_name)
        card_to_swap = self.card_repo.get_card(id_card)
        valid_result = True
        
        if (card_to_swap.name == "Cosa"):
            valid_result = False
        elif (card_to_swap.name == "Infectado"):
            num_infect = len(user.hand.select(lambda card : card.name == "Infectado"))

            if (user.role == "Humano"):
                valid_result = False
            elif (user.role == "Infectado" and num_infect == 1):
                valid_result = False
            elif (user.role == "Infectado" and target_user.role != "Cosa"):
                valid_result = False
  
        return valid_result

    @db_session
    def swap_card(self, lobby_name: str):
        user_start = self.game_repo.get_exchange_user_start(lobby_name)
        card_to_user_start_id = self.game_repo.get_exchange_card_user_finish(lobby_name)
        user_finish = self.game_repo.get_exchange_user_finish(lobby_name)
        card_to_user_finish_id = self.game_repo.get_exchange_card_user_start(lobby_name)
        self.discard_card(user_start, card_to_user_finish_id)
        self.user_repo.add_card_to_hand(user_finish, card_to_user_finish_id)
        self.discard_card(user_finish, card_to_user_start_id)
        self.user_repo.add_card_to_hand(user_start, card_to_user_start_id)
        self.game_repo.clean_exchange_data(lobby_name)
        
    @db_session
    def can_card_be_discarded(self, user_name: str, id_card: int) -> bool:
        user = self.user_repo.get_user(user_name)
        card_to_discard = self.card_repo.get_card(id_card)
        valid_result = True
        
        if (card_to_discard.name == "Cosa"):
            valid_result = False
        elif (card_to_discard.name == "Infectado"):
            num_infect = len(user.hand.select(lambda card : card.name == "Infectado"))
            if (user.role == "Infectado" and num_infect == 1):
                valid_result = False
       
        return valid_result

    @db_session
    def end_game(self, lobby_name: str):
        self.game_repo.remove_game(lobby_name)
        self.lobby_repo.remove_all_users_from_lobby(lobby_name)
        self.lobby_repo.remove_lobby(lobby_name)
        
    @db_session
    def superinfection(self, user_name: str) -> bool:
        user_hand = self.user_repo.get_user_hand(user_name)
        all_infected_cards = True
        for card in user_hand:
            all_infected_cards = all_infected_cards and (card.name == "Infectado")
        return all_infected_cards
        
    @db_session
    def exchange_with_superinfection(self, user_name: str, target_user_name: str) -> bool:
        user = self.user_repo.get_user(user_name)
        target_user = self.user_repo.get_user(target_user_name)
        exchange_with_superinfection = False
        if (self.superinfection(user_name) or self.superinfection(target_user_name)):
            if not ((user.role == "Infectado" and target_user.role == "Cosa") 
                    or (user.role == "Cosa" and target_user.role == "Infectado")):
                exchange_with_superinfection = True
    
        return exchange_with_superinfection
    
    @db_session
    def previous_player(self, game_name :str, user_name :str) -> User:
        user_position = self.position_repo.get_position(user_name)
        user_number = self.position_repo.get_number(user_position)
        amount_players = self.game_repo.get_amount_players(game_name)

        previous_position = None
        while previous_position == None:
            if user_number == 1:
                previous_position = self.game_repo.get_n_position(amount_players, game_name)
            else:
                previous_position = self.game_repo.get_n_position(user_number-1, game_name)

            if previous_position == None:
                user_number = (user_number % amount_players) + 1 # Si no hay siguiente, se busca el siguiente del siguiente
        
        previous_user = self.position_repo.get_user(previous_position)
        return previous_user
    
    @db_session
    def next_player(self, game_name :str, user_name :str) -> User:
        user_position = self.position_repo.get_position(user_name)
        user_number = self.position_repo.get_number(user_position)
        amount_players = self.game_repo.get_amount_players(game_name)

        next_position = None
        while next_position == None:
            next_position = self.game_repo.get_n_position((user_number % amount_players) + 1, game_name)

            if next_position == None:
                user_number = (user_number % amount_players) + 1 # Si no hay siguiente, se busca el siguiente del siguiente

        next_user = self.position_repo.get_user(next_position)
        return next_user

    @db_session
    def targets_according_action_obstacle_card(self, user_name: str, lobby_name: str, card_name: str) -> list[str]:
        #! No tiene en cuenta estado de cuarententa y puerta atrancada por el momento
        lobby_repo = LobbyRepository()
        all_players = lobby_repo.get_lobby_users_no_host(lobby_name)
        previous_user_name = self.previous_player(lobby_name, user_name).name
        next_user_name = self.next_player(lobby_name, user_name).name
        
        target_users = []
        match card_name:
            case "Hacha":   # No hay puerta atrancada ni cuarentena
                pass
            case "Determinacion": # Todavia no se implementa
                pass
            case "Mas vale que corras" | "Seduccion": # Todos menos el que la juega
                for user in all_players:
                    target_users.append(user["name"])
                target_users.remove(user_name)
            case "Whisky" | "Vigila tus espaldas":  # El que juega o el flujo de juego
                target_users.append(user_name)
            case "Lanzallamas" | "Analisis" | "Sospecha" | "Cambio de lugar" | "Cuarentena" | "Puerta trancada": # Usuarios adyacentes
                target_users.append(previous_user_name)
                target_users.append(next_user_name)
            
        return target_users
        
    @db_session
    def get_play_combinations(self, user_name: str, lobby_name: str) -> dict:
        user_hand = self.user_repo.get_user_hand(user_name)
        cards_with_targets = {}
        total_user_cards = len(user_hand)
        for i in range(0, total_user_cards):
            card_id = user_hand[i].id
            card_name = user_hand[i].name
            cards_with_targets[card_id] = self.targets_according_action_obstacle_card(user_name, lobby_name, card_name)
        return cards_with_targets

    @db_session
    def can_user_play(self, user_name: str, lobby_name: str) -> bool:
        cards_with_targets = self.get_play_combinations(user_name, lobby_name)
        combinations = 0
        for card in cards_with_targets:
            combinations = combinations + len(cards_with_targets[card])
        return (combinations > 0) and (not self.user_repo.is_user_in_quarantine(user_name))

    @db_session
    def is_card_in_hand(self, user_name: str, card_name: str) -> bool:
        user_hand = self.user_repo.get_user_hand(user_name)
        total_user_cards = len(user_hand)
        exist_card = False
        for i in range(0, total_user_cards):
            exist_card = exist_card or (user_hand[i]["name"] == card_name)
        return exist_card
        
    @db_session
    def can_user_defend_exchange(self, target_user_name: str) -> bool: #! Incluir Fallaste
        return self.is_card_in_hand(target_user_name, "Aterrador") or self.is_card_in_hand(target_user_name, "No_gracias")

    @db_session
    def can_user_defend(self, target_user_name: str, card_name: str) -> bool:
        defense = False
        match card_name:
            case "Seduccion": 
                defense = self.can_user_defend_exchange(target_user_name)
            case "Cambio de lugar" | "Mas vale que corras":
                defense = self.is_card_in_hand(target_user_name, "Aqui estoy bien")
            case "Lanzallamas":
                defense = self.is_card_in_hand(target_user_name, "Nada de barbacoas")

        return defense

    @db_session
    def can_card_cancel_effect(self, lobby_name: str, card_name: str)-> bool:
        card_effect = self.game_repo.get_effect_to_be_applied
        cancel = False
        match card_effect:
            case "Seduccion" | "swap_card":
                cancel = (card_name == "Aterrador") or (card_name == "No_gracias")
            case "Cambio de lugar" | "Mas vale que corras":
                cancel = (card_name == "Aqui estoy bien")
            case "Lanzallamas":
                cancel = (card_name == "Nada de barbacoas")
        return cancel

    @db_session
    def is_there_obstacle(self, lobby_name: str, user_name: str) -> bool:
        direction = self.game_repo.get_direction(lobby_name)
        if (direction):
            result = self.position_repo.get_right_door(user_name)
        else:
            result = self.position_repo.get_left_door(user_name)
        return result

    @db_session
    def is_there_obstacle_between_players(self, lobby_name: str, user_name: str, target_user_name: str) -> bool:
        pos_user = self.position_repo.get_numb_position(user_name)
        pos_target = self.position_repo.get_numb_position(target_user_name)
        amount_players = self.lobby_repo.get_amount_users
        obstacle = False
        if((pos_user == 1 and pos_target == amount_players) or
            pos_user > pos_target):
            obstacle = self.position_repo.get_left_door(user_name) and self.position_repo.get_right_door(target_user_name)
        else:
            obstacle = self.position_repo.get_left_door(target_user_name) and self.position_repo.get_right_door(user_name)

        return obstacle