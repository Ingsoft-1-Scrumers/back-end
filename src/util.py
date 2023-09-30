from repository import *

class GameLogic:

    def start_game(self, lobby_name: str):
        lobby_repo = LobbyRepository()
        game_repo = GameRepository()
        card_repo = CardRepository()

        lobby = lobby_repo.get_lobby(lobby_name)
        user_amount = lobby_repo.get_amount_users(lobby_name)
        game = lobby_repo.get_game(lobby_name)
        users = lobby_repo.get_lobby_users(lobby_name)
        
        game_repo.create_game(lobby, user_amount)
        card_repo.create_deck(game)
        card_repo.deal_cards_all_users(lobby_name)
        self.assign_positions(users, game)
        self.assign_turn(user_amount, game)

    def assign_positions(self, users: Set(User), game: Game):
        position_repo = PositionRepository()
        for user in users:
            position_repo.create_position(user, game)

    def assign_turn(self, game: Game):
        game_repo = GameRepository()
        positions = game_repo.get_all_positions(game)
        position = positions.random(1)[0]
        game_repo.assign_turn(position, game)