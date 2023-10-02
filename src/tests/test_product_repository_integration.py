import pytest
from pony.orm import count, db_session
from template import ALL_TEMPLATES

from models import User
from repository import *

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
        assert count(User.select()) == N_users + 1
        

@pytest.mark.integration_test
def test_get_user(user_repository: UserRepository):
        
        with db_session:
            user = user_repository.get_user('User_A')
        
        with db_session:
            assert user.name == 'User_A'

@pytest.mark.integration_test
def test_user_exists(user_repository: UserRepository):
        
        with db_session:
            assert user_repository.user_exists('User_A')

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
            assert user_repository.is_user_host('ABCD_lobby', 'User_A')


@pytest.mark.integration_test
def test_create_lobby(lobby_repository: LobbyRepository):
    
    with db_session:
        N_lobby = count(Lobby.select()) 
    
    lobby_repository.create_lobby("extra_lobby", 3, 4, "a_difficult_password", "User_N")
    
    with db_session:
        assert count(Lobby.select()) == N_lobby + 1

@pytest.mark.integration_test
def test_get_lobby(lobby_repository: LobbyRepository):
        
        with db_session:
            lobby = lobby_repository.get_lobby("ABCD_lobby")
        
        with db_session:
            assert lobby.name == "ABCD_lobby"
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
            assert min_players == 4

@pytest.mark.integration_test
def test_get_max_players(lobby_repository: LobbyRepository):
        
        with db_session:
            max_players = lobby_repository.get_max_players("ABCD_lobby")
        
        with db_session:
            assert max_players == 5
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
            assert host_name == "User_A"

@pytest.mark.integration_test
def test_get_amount_users(lobby_repository: LobbyRepository):
        
        with db_session:
            amount_users = lobby_repository.get_amount_users("ABCD_lobby")

        with db_session:
            assert amount_users == count(User.select().where(lambda u: u.lobby.name == "ABCD_lobby"))

@pytest.mark.integration_test
def test_lobby_exists(lobby_repository: LobbyRepository):
        
        with db_session:
            assert lobby_repository.lobby_exists("ABCD_lobby")

@pytest.mark.integration_test
def test_create_game(game_repository: GameRepository):
    
    with db_session:
        N_game = count(Game.select()) 
        game_repository.create_game("ABCD_lobby", 4)
    
    with db_session:
        assert count(Game.select()) == N_game + 1
        
@pytest.mark.integration_test
def test_get_game(game_repository: GameRepository):
        
        with db_session:
            game = game_repository.get_game("ABCD_lobby")
        
        with db_session:
            assert game.name == "ABCD_lobby"

@pytest.mark.integration_test
def test_get_amount_players(game_repository: GameRepository):
        
        with db_session:
            amount_players = game_repository.get_amount_players("ABCD_lobby")

        with db_session:
            assert amount_players == 4


@pytest.mark.integration_test
def test_create_card(card_repository: CardRepository):
    
    with db_session:
        N_cards = count(Card.select()) 
        card_repository.create_card(ALL_TEMPLATES[0], Game[Lobby["ABCD_lobby"]])
    
    with db_session:
        assert count(Card.select()) == N_cards + 1

@pytest.mark.integration_test
def test_get_card(card_repository: CardRepository):
        
        with db_session:
            card = card_repository.get_card(1)
        
        with db_session:
            assert card.name == "La cosa"

@pytest.mark.integration_test
def test_create_position(position_repository: PositionRepository):
    
    with db_session:
        N_positions = count(Position.select())
        position_repository.create_position(User['User_A'], 1, Game[Lobby["ABCD_lobby"]])

    with db_session:
        assert count(Position.select()) == N_positions + 1

