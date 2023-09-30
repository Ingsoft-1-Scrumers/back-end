import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app import app

client = TestClient(app) #para realizar solicitudes HTTP 

#una fixture es un conjunto de datos predefinidos y/o configuración necesaria que se utiliza para preparar el estado inicial de una prueba
@pytest.fixture
def user_a():
    return {"name": "Miguel"}

#patch sirve para aclarar que UserRepository se va a reemplazar por un mock
@patch('app.UserRepository')
def test_create_user(mock_UserRepository, user_a):
    mock_repository = MagicMock() #Crea una instancia de MagicMock, que simulará un objeto UserRepository
    mock_repository.create_user.return_value = user_a #Configura el comportamiento del método create_user del mock
    mock_UserRepository.return_value = mock_repository #: Configura el mock "mock_UserRepository" para devolver la instancia del mock mock_repository cuando se cree una nueva instancia de UserRepository

    response = client.post("/create_user/?user_name=Miguel")
    assert response.status_code == 200
    assert response.json() == {'message': 'User created'}


@patch('app.GameRepository')
@patch('app.LobbyRepository')
def test_start_game(mock_LobbyRepository, mock_GameRepository):
    mock_repository = MagicMock()
    mock_repository.create_Game.return_value = "Game started successfully"
    mock_GameRepository.return_value = mock_repository

    mock_repository = MagicMock()
    mock_repository.amount_players.return_value = 4
    mock_LobbyRepository.return_value = mock_repository

    response = client.post("/start_game/?game_name=Game1")
    assert response.status_code == 200
    assert response.json() == {'message': 'Game started successfully'}


