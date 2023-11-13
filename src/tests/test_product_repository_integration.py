import pytest
from pony.orm import count, db_session
from template import ALL_TEMPLATES

from models import User
from repository import *
from util import *

@pytest.fixture
def user_repository():
    return UserRepository()

@pytest.fixture
def lobby_repository():
    return LobbyRepository()

@pytest.fixture
def game_repository():
    return GameRepository()

@pytest.fixture
def card_repository():
    return CardRepository()

@pytest.fixture
def position_repository():
    return PositionRepository()

@pytest.fixture
def game_logic():
    return GameLogic()

"""
Prueba de integracion:
Insertar un nuevo producto en la base de datos y aumentar la cantidad total de usuarios en uno
"""

@pytest.mark.integration_test
def test_create_user(user_repository: UserRepository):

    with db_session:
        N_users = count(User.select()) 

    user_repository.create_user('User_N')

    with db_session:
        assert count(User.select()) == N_users + 1, "User count was not incremented correctly"
        

@pytest.mark.integration_test
def test_get_user(user_repository: UserRepository):
        
        with db_session:
            user = user_repository.get_user('User_A')
        
        with db_session:
            assert user.name == 'User_A', "The user name obtained does not match 'User_A'"

@pytest.mark.integration_test
def test_user_exists(user_repository: UserRepository):
        
        with db_session:
            assert user_repository.user_exists('User_A'), "User 'User_A' should exist in the repository"

'''        
@pytest.mark.integration_test
def test_is_user_in_a_lobby(user_repository: UserRepository):
        
        with db_session:
            assert user_repository.is_user_in_a_lobby('User_A')
'''
'''
@pytest.mark.integration_test
def test_is_user_in_lobby(user_repository: UserRepository):
        
        with db_session:
            assert user_repository.is_user_in_lobby('ABCD_lobby', 'User_A')
'''

@pytest.mark.integration_test
def test_is_user_host(user_repository: UserRepository):
        
        with db_session:
            assert user_repository.is_user_host('ABCD_lobby', 'User_A'), "User_A should be the host of lobby 'ABCD_lobby'"


@pytest.mark.integration_test
def test_create_lobby(lobby_repository: LobbyRepository):
    
    with db_session:
        N_lobby = count(Lobby.select()) 
    
    lobby_repository.create_lobby("extra_lobby", 3, 4, "a_difficult_password", "User_N")
    
    with db_session:
        assert count(Lobby.select()) == N_lobby + 1, "An additional lobby should have been created"

@pytest.mark.integration_test
def test_get_lobby(lobby_repository: LobbyRepository):
        
        with db_session:
            lobby = lobby_repository.get_lobby("ABCD_lobby")
        
        with db_session:
            assert lobby.name == "ABCD_lobby", "Lobby 'ABCD_lobby' should have been fetched correctly"
'''
@pytest.mark.integration_test
def test_get_lobby_set_users(lobby_repository: LobbyRepository):
        
        with db_session:
            lobby = lobby_repository.get_lobby("ABCD_lobby")
        
        with db_session:
            assert len(lobby.users) == 1
'''

@pytest.mark.integration_test
def test_get_min_players(lobby_repository: LobbyRepository):
        
        with db_session:
            min_players = lobby_repository.get_min_players("ABCD_lobby")
        
        with db_session:
            assert min_players == 4, "The minimum number of players should have been obtained correctly (4)"

@pytest.mark.integration_test
def test_get_max_players(lobby_repository: LobbyRepository):
        
        with db_session:
            max_players = lobby_repository.get_max_players("ABCD_lobby")
        
        with db_session:
            assert max_players == 5, "Should have retrieved the maximum number of players correctly (5)"
'''
@pytest.mark.integration_test
def test_get_password(lobby_repository: LobbyRepository):
        
        with db_session:
            password = lobby_repository.get_password("ABCD_lobby")
        
        with db_session:
            assert password == "a_difficult_password"
'''
@pytest.mark.integration_test
def test_get_host_name(lobby_repository: LobbyRepository):
        
        with db_session:
            host_name = lobby_repository.get_host_name("ABCD_lobby")
        
        with db_session:
            assert host_name == "User_A", "Should have retrieved the host name as 'User_A'"

@pytest.mark.integration_test
def test_get_amount_users(lobby_repository: LobbyRepository):
        
        with db_session:
            amount_users = lobby_repository.get_amount_users("ABCD_lobby")

        with db_session:
            assert amount_users == count(User.select().where(lambda u: u.lobby.name == "ABCD_lobby")), "The amount of users should match the expected amount"

@pytest.mark.integration_test
def test_lobby_exists(lobby_repository: LobbyRepository):
        
        with db_session:
            assert lobby_repository.lobby_exists("ABCD_lobby"), "Lobby 'ABCD_lobby' should exist in the repository"

@pytest.mark.integration_test
def test_create_game(game_repository: GameRepository):
    
    with db_session:
        N_game = count(Game.select()) 
        game_repository.create_game("ABCD_lobby", 4)
    
    with db_session:
        assert count(Game.select()) == N_game + 1, "An additional game should have been created"
        
@pytest.mark.integration_test
def test_is_game_started(lobby_repository: LobbyRepository):
     
     with db_session:
          assert lobby_repository.is_game_started("ABCD_lobby") == True, "The game was created correctly"

@pytest.mark.integration_test
def test_get_game(game_repository: GameRepository):
        
        with db_session:
            game = game_repository.get_game("ABCD_lobby")
        
        with db_session:
            assert game.name == "ABCD_lobby", "Game 'ABCD_lobby' should have been fetched correctly"

@pytest.mark.integration_test
def test_get_amount_players(game_repository: GameRepository):
        
        with db_session:
            amount_players = game_repository.get_amount_players("ABCD_lobby")

        with db_session:
            assert amount_players == 4, "The amount of players should match the expected amount"


@pytest.mark.integration_test
def test_create_card(card_repository: CardRepository):
    
    with db_session:
        N_cards = count(Card.select()) 
        card_repository.create_card(ALL_TEMPLATES[0], Game[Lobby["ABCD_lobby"]])
    
    with db_session:
        assert count(Card.select()) == N_cards + 1, "An additional card should have been created"

@pytest.mark.integration_test
def test_get_card(card_repository: CardRepository):
        
        with db_session:
            card = card_repository.get_card(1)
        
        with db_session:
            assert card.name == "Cosa", "Card 'Cosa' should have been fetched correctly"

@pytest.mark.integration_test
def test_create_position(position_repository: PositionRepository):
    
    with db_session:
        N_positions = count(Position.select())
        position_repository.create_position(User['User_A'], 1, Game[Lobby["ABCD_lobby"]])

    with db_session:
        assert count(Position.select()) == N_positions + 1, "An additional position should have been created"


@pytest.mark.integration_test
def test_start_and_end_game(game_logic: GameLogic):
    
    with db_session:
        N_lobby = count(Lobby.select())

    game_logic.start_game("1234_lobby")
    with db_session:
        N_game = count(Game.select())
        N_cards = count(Card.select())
        N_positions = count(Position.select())
        assert N_cards > 0, "There should be cards in the database"
        assert N_positions > 0, "There should be positions in the database"

    game_logic.end_game("1234_lobby")
    
    with db_session:
        assert count(Game.select()) == N_game - 1, "The game should have been deleted"
        assert count(Lobby.select()) == N_lobby - 1, "The lobby should have been deleted"
        assert count(Card.select()) == N_cards - 54, "The cards should have been deleted"
        assert count(Position.select()) == N_positions - 4, "The positions should have been deleted"
