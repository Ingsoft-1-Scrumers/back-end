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
def test_create_lobby(lobby_repository: LobbyRepository):
    
    with db_session:
        N_lobby = count(Lobby.select()) 
    
    lobby_repository.create_lobby("extra_lobby", 3, 4, "a_difficult_password", "User_N")
    
    with db_session:
        assert count(Lobby.select()) == N_lobby + 1

@pytest.mark.integration_test
def test_create_game(game_repository: GameRepository):
    
    with db_session:
        N_game = count(Game.select()) 
        game_repository.create_game("ABCD_lobby", 4)
    
    with db_session:
        assert count(Game.select()) == N_game + 1
        
@pytest.mark.integration_test
def test_create_card(card_repository: CardRepository):
    
    with db_session:
        N_cards = count(Card.select()) 
        card_repository.create_card(ALL_TEMPLATES[0], Game[Lobby["ABCD_lobby"]])
    
    with db_session:
        assert count(Card.select()) == N_cards + 1