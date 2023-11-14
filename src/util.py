from repository import *
from settings import CARDS_PER_USER
from template import ALL_TEMPLATES

@db_session
def vigila_tus_espaldas(game_name: str, user_name: str, target_user_name: str):
    game_repo = GameRepository()
    direction = game_repo.get_direction(game_name)
    game_repo.set_direction(game_name, not direction)

@db_session
# Verificacion si target_user_name sigue vivo
def lanzallamas(game_name: str, user_name: str, target_user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()
    position_repo = PositionRepository()
    
    pos_target = position_repo.get_position_user_name(target_user_name)
    
    # 1 (2) | 3 4 5 -> 1 | 3 4 5 -> el 3 sigue con la puerta a izq, falta puerta der en 1
    if (position_repo.get_right_door(pos_target)):
        left_player_of_target_name = game_logic.closest_anticlockwise_player(game_name, target_user_name)
        left_player_of_target_pos = position_repo.get_position(left_player_of_target_name)
        position_repo.set_right_door(pos_target, False)
        position_repo.set_right_door(left_player_of_target_pos, True)
        
    # 1 2 | (3) 4 5 -> 1 2 | 4 5 -> el 2 sigue con la puerta a der, falta puerta izq en 4
    if (position_repo.get_left_door(pos_target)):
        right_player_of_target_name = game_logic.closest_clockwise_player(game_name, target_user_name)
        right_player_of_target_pos = position_repo.get_position(right_player_of_target_name)
        position_repo.set_left_door(pos_target, False)
        position_repo.set_left_door(right_player_of_target_pos, True)

    target_user = user_repo.get_user(target_user_name)
    # Si se quiere eliminar al host, se cambia el mismo
    if (user_repo.is_user_host(game_name, target_user_name)):
        lobby_repo.change_host(game_name, user_name)
    # Descarto las cartas
    hand = user_repo.get_user_hand_int(target_user_name)
    for card in hand:
        game_logic.discard_card_from_hand(target_user, card)
    user_repo.user_death(target_user_name)

@db_session
def cambio_de_lugar(game_name: str, user_name: str, target_user_name: str):
    game_logic = GameLogic()
    game_logic.swap_positions(user_name, target_user_name)

@db_session
def hacha(game_name: str, user_name: str, target_user_name: str):
    user_repo = UserRepository()
    position_repo = PositionRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()

    if(user_name == target_user_name):
        user_repo.set_user_in_quarantine_false(target_user_name)
    else:
        #sacamos la puerta atrancada entre el user y el target
        if(game_logic.is_there_obstacle_between_players(game_name, user_name, target_user_name)):
            pos_user_numb = position_repo.get_numb_position(user_name)
            pos_target_numb = position_repo.get_numb_position(target_user_name)
            amount_players = lobby_repo.get_amount_users(game_name)
            pos_user = position_repo.get_position_user_name(user_name)
            pos_target = position_repo.get_position_user_name(target_user_name)

            if((pos_user_numb == 1 and pos_target_numb == amount_players) or
                pos_user_numb > pos_target_numb):
                position_repo.set_left_door(pos_user, False)
                position_repo.set_right_door(pos_target, False)
            else:
                position_repo.set_left_door(pos_target, False)
                position_repo.set_right_door(pos_user, False)
        #sacamos la cuarentena del adyacente
        elif(user_repo.is_user_in_quarantine(target_user_name)):
            user_repo.set_user_in_quarantine_false(target_user_name)

@db_session
def determinacion(game_name: str, user_name: str, target_user_name: str):
    pass

@db_session
def cuarentena(game_name: str, user_name: str, target_user_name: str):
    position_repo = PositionRepository()
    user_repo = UserRepository()
    pos_user = position_repo.get_numb_position(user_name)
    pos_target = position_repo.get_numb_position(target_user_name)

    if (pos_user < pos_target):
        user_repo.set_user_in_quarantine_next_player(target_user_name) 
    else:
        user_repo.set_user_in_quarantine_previous_player(target_user_name)

@db_session
def puerta_atrancada(game_name: str, user_name: str, target_user_name: str):
    position_repo = PositionRepository()
    lobby_repo = LobbyRepository()
    pos_user = position_repo.get_numb_position(user_name)
    pos_target = position_repo.get_numb_position(target_user_name)
    amount_players = lobby_repo.get_amount_users(game_name)
    user_pos = position_repo.get_position_user_name(user_name)
    target_pos = position_repo.get_position_user_name(target_user_name)

    if ((pos_user == 1 and pos_target == amount_players)):
        position_repo.set_right_door(target_pos, True)
        position_repo.set_left_door(user_pos, True)
    elif(pos_user == amount_players and pos_target == 1):
        position_repo.set_right_door(user_pos, True)
        position_repo.set_left_door(target_pos, True)
    elif(pos_user > pos_target):
        position_repo.set_right_door(target_pos, True)
        position_repo.set_left_door(user_pos, True)
    else:
        position_repo.set_right_door(user_pos, True)
        position_repo.set_left_door(target_pos, True)

# Luego generamos el diccionario

ALL_EFFECTS = { #cartas de acción y obstáculo
#ACCIÓN
    "Vigila tus espaldas": vigila_tus_espaldas,
    "Lanzallamas": lanzallamas,
    "Cambio de lugar": cambio_de_lugar,
    "Mas vale que corras": cambio_de_lugar,
    "Hacha": hacha,
    "Determinacion": determinacion,
#OBSTÁCULO
    "Cuarentena": cuarentena,
    "Puerta trancada": puerta_atrancada
}


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
            if user.role == "Cosa":
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
        initial_amount_players = self.game_repo.get_initial_amount(lobby_name)
        actual_turn = self.game_repo.get_turn(lobby_name)
        position_number = actual_turn.number

        user_name = self.position_repo.get_user_name_position(actual_turn)
        if(self.user_repo.is_user_in_quarantine(user_name)):
            self.user_repo.decrease_quarantine(user_name)

        new_turn_position = None
        while new_turn_position == None:
            if direction: # True = Sentido horario
                new_turn_position = self.game_repo.get_n_position((position_number % initial_amount_players) + 1, lobby_name)

                if (new_turn_position == None):
                    position_number = (position_number % initial_amount_players) + 1
                    
            else: # False = Sentido antihorario
                if position_number == 1:
                    new_turn_position = self.game_repo.get_n_position(initial_amount_players, lobby_name)
                    if (new_turn_position == None):
                        position_number = initial_amount_players
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
        self.swap_with_infect_effect(lobby_name, card_to_user_finish_id, card_to_user_start_id, user_start, user_finish)

    @db_session
    def swap_with_infect_effect(self, lobby_name :str, card_start_id: int, card_finish_id: int, user_start: str, user_finish: str):
        card_start = self.card_repo.get_card_name(card_start_id)
        card_finish = self.card_repo.get_card_name(card_finish_id)
        start_user = self.user_repo.get_user(user_start)
        finish_user = self.user_repo.get_user(user_finish)
        # more_than_one_human = self.more_than_one_human(lobby_name)
        if (card_start == "Infectado" and start_user.role == "Cosa"):
            self.user_repo.infect_effect(user_finish)
        elif (card_finish == "Infectado" and finish_user.role == "Cosa"):
            self.user_repo.infect_effect(user_start)

    @db_session
    def more_than_one_human(self, lobby_name: str) -> bool:
        users = self.lobby_repo.get_lobby_set_users(lobby_name)
        humans = 0
        for user in users:
            if (user.role == "Humano"):
                humans += 1
        return humans > 1
        
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
        elif(card_to_discard.type == "Panico"):
            valid_result = False
       
        return valid_result

    @db_session
    def end_game(self, lobby_name: str):
        self.delete_all_doors(lobby_name)
        self.delete_all_quarantine(lobby_name)
        self.game_repo.remove_game(lobby_name)
        self.lobby_repo.remove_all_users_from_lobby(lobby_name)
        self.lobby_repo.remove_lobby(lobby_name)

    @db_session
    def update_doors_after_swap_position(self, user_name1, user_name2):
        position_repo = PositionRepository()
        pos_user_1 = position_repo.get_position_user_name(user_name1)
        pos_user_2 = position_repo.get_position_user_name(user_name2)
        
        right_door_1 = position_repo.get_right_door(pos_user_1)
        right_door_2 = position_repo.get_right_door(pos_user_2)
        left_door_1 = position_repo.get_left_door(pos_user_1)
        left_door_2 = position_repo.get_left_door(pos_user_2)
        
        # 1 2 | 3 4 5 -> swap 2 y 5 -> 1 5 | 3 4 2
        if (right_door_1):
            position_repo.set_right_door(pos_user_1, False)
            position_repo.set_right_door(pos_user_2, True)
        if (right_door_2):
            position_repo.set_right_door(pos_user_2, False)
            position_repo.set_right_door(pos_user_1, True)
            
        # 1 2 | 3 4 5 -> swap 3 y 5 -> 1 2 | 5 4 3
        if (left_door_1):
            position_repo.set_left_door(pos_user_1, False)
            position_repo.set_left_door(pos_user_2, True)
        if (left_door_2):
            position_repo.set_left_door(pos_user_2, False)
            position_repo.set_left_door(pos_user_1, True)

    @db_session
    def swap_positions(self, user_name1: str, user_name2: str):
        pos_user1 = self.user_repo.get_position(user_name1)
        pos_user2 = self.user_repo.get_position(user_name2)
        
        aux1 = self.position_repo.get_number(pos_user1)
        aux2 = self.position_repo.get_number(pos_user2)
        
        self.update_doors_after_swap_position(user_name1, user_name2)

        self.position_repo.set_position(pos_user1, aux2)
        self.position_repo.set_position(pos_user2, aux1)
        
    @db_session
    def superinfection(self, user_name: str) -> bool:
        user_hand = self.user_repo.get_user_hand(user_name)
        all_infected_cards = True
        for card in user_hand:
            all_infected_cards = all_infected_cards and (card["name"] == "Infectado")
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
    def closest_clockwise_player(self, game_name: str, user_name: str) -> str:
        initial_amount_players = self.game_repo.get_initial_amount(game_name)
        user_position = self.position_repo.get_position(user_name)
        user_number = self.position_repo.get_number(user_position)
        left_position = None

        while left_position == None:
            left_position = self.game_repo.get_n_position((user_number % initial_amount_players) + 1, game_name)

            if left_position == None:
                user_number = (user_number % initial_amount_players) + 1 # Si no hay siguiente, se busca el siguiente del siguiente

        return left_position.user.name

    @db_session
    def closest_anticlockwise_player(self, game_name: str, user_name: str) -> str:
        initial_amount_players = self.game_repo.get_initial_amount(game_name)
        user_position = self.position_repo.get_position(user_name)
        user_number = self.position_repo.get_number(user_position)
        right_position = None

        while right_position == None:
            if user_number == 1:
                right_position = self.game_repo.get_n_position(initial_amount_players, game_name)
            else:
                right_position = self.game_repo.get_n_position(user_number-1, game_name)

            if right_position == None:
                if (user_number > 1):
                    user_number -= 1
                else:
                    user_number = initial_amount_players
            
        return right_position.user.name


    @db_session
    def previous_player(self, game_name :str, user_name :str) -> str:
        direction = self.game_repo.get_direction(game_name)

        if (direction): #sentido horario, el previous es la izquierda
            previous_player = self.closest_anticlockwise_player(game_name, user_name) 
        else: #sentido antihorario, el previous es la derecha
            previous_player = self.closest_clockwise_player(game_name, user_name)
            
        return previous_player
    
    @db_session
    def next_player(self, game_name :str, user_name :str) -> str:
        direction = self.game_repo.get_direction(game_name)

        if (direction): #sentido horario, el next es la derecha
            next_player = self.closest_clockwise_player(game_name, user_name)
        else: #sentido antihorario, el next es la izquierda
            next_player = self.closest_anticlockwise_player(game_name, user_name)
        
        return next_player

    @db_session
    def targets_according_action_obstacle_card(self, user_name: str, lobby_name: str, card_name: str) -> list[str]:
        lobby_repo = LobbyRepository()
        all_players = lobby_repo.get_lobby_users_no_host(lobby_name)
        previous_user_name = (self.previous_player(lobby_name, user_name))
        next_user_name = (self.next_player(lobby_name, user_name))
        
        target_users = []
        match card_name:
            case "Hacha":   
                if(self.user_repo.is_user_in_quarantine(user_name)):    #si estoy en cuarentena, puedo jugar esta carta sobre mi mismo
                    target_users.append(user_name)
                    
                #si hay puerta atrancada entre yo y un jugador adyacente, juego esa carta sobre el jugador para sacar la puerta
                #si mis adyacentes están en cuarentena, puedo jugarles esta carta
                if(self.is_there_obstacle_between_players(lobby_name, user_name, next_user_name)
                   or self.user_repo.is_user_in_quarantine(next_user_name)):
                    target_users.append(next_user_name)
                if(self.is_there_obstacle_between_players(lobby_name, user_name, previous_user_name)
                   or self.user_repo.is_user_in_quarantine(previous_user_name)):
                    target_users.append(previous_user_name)

            case "Mas vale que corras": 
                #no puede jugar la carta si estoy en cuarentena
                if(not self.user_repo.is_user_in_quarantine(user_name)):
                    for user in all_players:
                        #no puede con los que están en cuarentena
                        if(not self.user_repo.is_user_in_quarantine((user["name"])) and (user["name"] != user_name)):
                            target_users.append(user["name"])

            case "Seduccion": # Todos menos el que la juega
                for user in all_players:
                    #no puede con los que están en cuarentena
                    if(not self.user_repo.is_user_in_quarantine((user["name"])) and (user["name"] != user_name)):
                        target_users.append(user["name"])

            case "No podemos ser amigos" | "Sal de aqui": # Todos menos el que la juega
                for user in all_players:
                    #no puede con los que están en cuarentena
                    if(not self.user_repo.is_user_in_quarantine((user["name"])) and (user["name"] != user_name)):
                        target_users.append(user["name"])
                if (len(target_users) == 0):
                    target_users.append(user_name)

            case "Whisky" | "Vigila tus espaldas" | "¡Ups!" | "Cita a ciegas":  # El que juega o el flujo de juego
                target_users.append(user_name)
            
            case "Lanzallamas":
                #no puedo jugar si estoy en cuarentena
                if(not self.user_repo.is_user_in_quarantine(user_name)):
                    if(not self.is_there_obstacle_between_players(lobby_name, user_name, next_user_name)):
                        target_users.append(next_user_name)
                    if(not self.is_there_obstacle_between_players(lobby_name, user_name, previous_user_name)):
                        target_users.append(previous_user_name)

            case "Analisis" | "Sospecha" | "Cuarentena" | "Puerta trancada": # Usuarios adyacentes
                if(not self.is_there_obstacle_between_players(lobby_name, user_name, next_user_name)):
                    target_users.append(next_user_name)
                if(not self.is_there_obstacle_between_players(lobby_name, user_name, previous_user_name)):
                    target_users.append(previous_user_name)
                    
            case "Cambio de lugar":
                #no puedo jugar esta carta si estoy en cuarentena
                if (not self.user_repo.is_user_in_quarantine(user_name)):
                    if (not (self.is_there_obstacle_between_players(lobby_name, user_name, next_user_name) or self.user_repo.is_user_in_quarantine(next_user_name))):
                        target_users.append(next_user_name)
                    if (not (self.is_there_obstacle_between_players(lobby_name, user_name, previous_user_name) or self.user_repo.is_user_in_quarantine(previous_user_name))):
                        target_users.append(previous_user_name)
            
            case "Que quede entre nosotros":
                target_users.append(next_user_name)
                target_users.append(previous_user_name)
                
            case "Determinacion" | "Revelaciones" | "Vuelta y vuelta" | "Olvidadizo" | "Es aqui la fiesta" | "Tres, cuatro" | "Cuerdas podridas":
                target_users.append(user_name)

            case "Uno, dos":
                previous_previous_user_name = self.previous_player(lobby_name, previous_user_name)
                next_next_user_name = self.next_player(lobby_name, next_user_name)
                if (next_next_user_name != user_name):
                    target_users.append(next_next_user_name)
                if (previous_previous_user_name != user_name):
                    target_users.append(previous_previous_user_name)
                if (len(target_users) == 0):
                    target_users.append(user_name)

        return target_users
        
    @db_session
    def get_play_combinations(self, user_name: str, lobby_name: str) -> [dict]:
        user_hand = self.user_repo.get_user_hand(user_name)
        cards_with_targets_and_discard = []
        total_user_cards = len(user_hand)
        for i in range(0, total_user_cards):
            cards_with_targets = {}
            card_id = user_hand[i]["id"]
            card_name = user_hand[i]["name"]
            cards_with_targets["card_id"] = card_id
            cards_with_targets["valid"] = self.targets_according_action_obstacle_card(user_name, lobby_name, card_name)
            cards_with_targets["discard"] = self.can_card_be_discarded(user_name, card_id)
            cards_with_targets_and_discard.append(cards_with_targets)
        return cards_with_targets_and_discard

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
            exist_card = exist_card or ((user_hand[i])["name"] == card_name)
        return exist_card
        
    @db_session
    def can_user_defend_exchange(self, target_user_name: str) -> bool:
        return self.is_card_in_hand(target_user_name, "Aterrador") or self.is_card_in_hand(target_user_name, "No_gracias") or self.is_card_in_hand(target_user_name, "Fallaste")

    @db_session
    def can_user_defend_play(self, target_user_name: str, card_name: str) -> bool:
        defense = False
        match card_name:
            case "Cambio de lugar":
                defense = self.is_card_in_hand(target_user_name, "Aqui estoy bien")
            case "Lanzallamas":
                defense = self.is_card_in_hand(target_user_name, "Nada de barbacoas")

        return defense

    @db_session
    def can_card_cancel_effect(self, lobby_name: str, card_name: str)-> bool:
        card_effect = self.game_repo.get_effect_to_be_applied(lobby_name)
        cancel = False
        match card_effect:
            case "Seduccion" | "swap_card":
                cancel = (card_name == "Aterrador") or (card_name == "No_gracias") or (card_name == "Fallaste")
            case "Cambio de lugar" | "Mas vale que corras":
                cancel = (card_name == "Aqui estoy bien")
            case "Lanzallamas":
                cancel = (card_name == "Nada de barbacoas")
        return cancel

    @db_session
    def is_there_obstacle(self, lobby_name: str, user_name: str) -> bool:
        direction = self.game_repo.get_direction(lobby_name)
        pos_user = self.position_repo.get_position_user_name(user_name)
        if (direction):
            result = self.position_repo.get_right_door(pos_user)
        else:
            result = self.position_repo.get_left_door(pos_user)
        return result

    #supone que son adyacentes.
    @db_session
    def is_there_obstacle_between_players(self, lobby_name: str, user_name: str, target_user_name: str) -> bool:
        pos_user_numb = self.position_repo.get_numb_position(user_name)
        pos_target_numb = self.position_repo.get_numb_position(target_user_name)
        amount_players = self.lobby_repo.get_amount_users(lobby_name)
        pos_user = self.position_repo.get_position_user_name(user_name)
        pos_target = self.position_repo.get_position_user_name(target_user_name)

        obstacle = False
        if((pos_user_numb == 1 and pos_target_numb == amount_players) or
            pos_user_numb > pos_target_numb):
            obstacle = self.position_repo.get_left_door(pos_user) and self.position_repo.get_right_door(pos_target)
        else:
            obstacle = self.position_repo.get_left_door(pos_target) and self.position_repo.get_right_door(pos_user)

        return obstacle

    @db_session
    def play_card(self, lobby_name: str, user_name: str, target_user_name: str, card_name: str):
        ALL_EFFECTS[card_name](lobby_name, user_name, target_user_name)


    @db_session
    def humans_win(self, lobby_name: str) -> bool:
        users = self.lobby_repo.get_lobby_set_users(lobby_name)
        is_there_cosa = False
        for user in users:
            if (user.role == "Cosa"):
                is_there_cosa = True
        return (not is_there_cosa)
    
    @db_session
    def cosa_win(self, lobby_name: str) -> bool:
        users = self.lobby_repo.get_lobby_set_users(lobby_name)
        is_there_humans = False
        for user in users:
            if (user.role == "Humano"):
                is_there_humans = True
        return (not is_there_humans)

    @db_session
    def victory(self, lobby_name: str) -> bool:
        return self.humans_win(lobby_name) or self.cosa_win(lobby_name)

    @db_session
    def team_winners(self, lobby_name: str) -> str:
        if (self.humans_win(lobby_name)):
            winners = "los humanos"
        else:
            winners = "la Cosa y los infectados"
        return winners
    
    @db_session
    def list_winners(self, lobby_name: str) -> [str]:
        humans = []
        cosa_and_infected = []
        users = self.lobby_repo.get_lobby_set_users(lobby_name)
        for user in users:
            if (user.role == "Humano"):
                humans.append(user.name)
            else:
                cosa_and_infected.append(user.name)
        if (self.humans_win(lobby_name)):
            winners = humans
        else:
            winners = cosa_and_infected
        return winners
    
    @db_session
    def flamethrower_lose_condition(self, user_name : str) -> bool:
        user_repo = UserRepository()
        
        death_condition = user_repo.get_role(user_name) == "Cosa" and self.is_card_in_hand(user_name, "Lanzallamas")
        return death_condition
    
    @db_session
    def delete_all_quarantine(self, lobby_name: str):
        user_repo = UserRepository()
        lobby_repo = LobbyRepository()
        all_players = lobby_repo.get_lobby_users_no_host(lobby_name)
        for user in all_players:
            user_repo.set_user_in_quarantine_false(user["name"])

    @db_session
    def delete_all_doors(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        position_repo = PositionRepository()
        all_players = lobby_repo.get_lobby_users_no_host(lobby_name)
        for user in all_players:
            pos_user = position_repo.get_position_user_name(user["name"])
            position_repo.set_left_door(pos_user, False)
            position_repo.set_right_door(pos_user, False)
    
    @db_session
    def swap_position_party(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        all_players = lobby_repo.get_lobby_users_no_host(lobby_name)
        length_players = len(all_players)
        for pair in range(0, (length_players//2)):
            first_user_of_pair = all_players[2*pair]["name"]
            second_user_of_pair = all_players[2*pair + 1]["name"]
            self.swap_positions(first_user_of_pair, second_user_of_pair)