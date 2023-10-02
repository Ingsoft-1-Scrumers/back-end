from repository import *

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
        self.assign_positions(users, game)
        self.assign_turn(game, 1)

    @db_session
    def assign_positions(self, users: Set(User), game: Game):
        position_repo = PositionRepository()
        num_order = 1
        for user in users:
            position_repo.create_position(user, num_order, game)
            num_order += 1

    @db_session #! Revisar acoplamiento y cohesion en el if
    def next_turn(self, game: Game):
        game_repo = GameRepository()
        position_repo = PositionRepository()
        amount_players = game_repo.get_amount_players(game)
        actual_turn = game_repo.get_turn(game)
        position_number = position_repo.get_number(actual_turn)
        
        if(position_number != amount_players):
            new_turn = Position.select(number=(position_number+1))
            game.turn = new_turn.first()
        else:
            new_turn = Position.select(number=1)
            game.turn = new_turn.first()

    @db_session
    def play_card(self, user_name: str, id_card: int, lobby_name: str):
        user_repo = UserRepository()
        lobby_repo = LobbyRepository()
        card_repo = CardRepository()
        user = user_repo.get_user(user_name)
        game = lobby_repo.get_game(lobby_name)
        card_repo.discard_card_from_hand(user, id_card)
        self.next_turn(game)

    @db_session
    def assign_turn(self, game: Game, num: int):
        game_repo = GameRepository()
        pos_n = game_repo.get_n_position(num, game)
        game_repo.assign_turn(pos_n, game)