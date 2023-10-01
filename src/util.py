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
    def assign_turn(self, game: Game):
        position_repo = PositionRepository()
        pos_1 = position_repo.get_n_position(1, game)
        game_repo = GameRepository()
        game_repo.assign_turn(pos_1, game)