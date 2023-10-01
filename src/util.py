from repository import *
import random

class GameLogic:

    @db_session
    def start_game(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        game_repo = GameRepository()
        card_repo = CardRepository()

        lobby = lobby_repo.get_lobby(lobby_name)
        user_amount = lobby_repo.get_amount_users(lobby_name)
        game_repo.create_game(lobby, user_amount)
        game = lobby_repo.get_game(lobby_name)
        users = lobby_repo.get_lobby_set_users(lobby_name)
        
        card_repo.create_deck(game)
        card_repo.deal_cards_all_users(lobby_name)
        self.assign_positions(users, user_amount, game)
        self.assign_turn(game)
        
    @db_session
    def assign_positions(self, users: Set(User), user_amount, game: Game):
        position_repo = PositionRepository()
        list_pos = [i for i in range(1, user_amount + 1)]
        random.shuffle(list_pos)
        for user in users:
            num = list_pos.pop()
            position_repo.create_position(user, num, game)
            
    @db_session
    def assign_positions(self, users: Set(User), game: Game):
        position_repo = PositionRepository()
        num_order = 1
        for user in users:
            position_repo.create_position(user, num_order, game)
            num_order += 1

    @db_session
    def next_turn(self, game: Game):
        amount_players = game.amount_players
        actual_turn = game.turn
        position_number = actual_turn.number
        
        if(position_number != amount_players):
            new_turn = Position.select(number=(position_number+1))
            game.turn = new_turn.first()
        else:
            new_turn = Position.select(number=1)
            game.turn = new_turn.first()

    @db_session
    def play_card(self, user_name: str, card: Card, lobby_name: str):
        user = User.get(name=user_name)
        lobby = Lobby.get(name=lobby_name)
        card_repo = CardRepository()
        card_repo.discard_card_from_hand(user, card)
        self.next_turn(lobby.game)

    @db_session
    def assign_turn(self, game: Game, num: int):
        position_repo = PositionRepository()
        pos_n = position_repo.get_n_position(num, game)
        game_repo = GameRepository()
        game_repo.assign_turn(pos_n, game)