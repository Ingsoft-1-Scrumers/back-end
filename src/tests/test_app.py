import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app import app

client = TestClient(app)

@pytest.fixture
def user():
    return {"name": "User1"}

@pytest.fixture
def lobby():
    return {"name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}

@pytest.fixture
def lobby_players():
    return {"name": "User1", "name" : "User2", "name" : "User3", "name" : "User4", "host": "User1"}

# Create user tests
@patch('app.UserRepository')
def test_create_user(mock_UserRepository, user):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = False
    mock_repository.create_user.return_value = user

    mock_UserRepository.return_value = mock_repository

    response = client.post("/create_user/?user_name=User1")
    assert response.status_code == 200
    assert response.json() == {'message': 'User created'}

@patch('app.UserRepository')
def test_create_user__user_already_exists(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = True

    mock_UserRepository.return_value = mock_repository

    response = client.post("/create_user/?user_name=User1")
    assert response.status_code == 400
    assert response.json() == {'detail': 'This username already exists'}

@patch('app.UserRepository')
def test_create_user__error(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = False
    mock_repository.create_user.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository

    response = client.post("/create_user/?user_name=User1")
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while creating the user'}

# Create lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_create_lobby(mock_UserRepository, mock_LobbyRepository, lobby):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    
    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = False
    mock_repository_lobby.create_lobby.return_value = lobby

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/create_lobby/?lobby_name=Lobby1&min_players=4&max_players=12&password=empty&host_name=User1')
    assert response.status_code == 200
    assert response.json() == {'message': 'Lobby created'}

@patch('app.UserRepository')
def test_create_lobby__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    response = client.post('/create_lobby/?lobby_name=Lobby1&min_players=4&max_players=12&password=empty&host_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This user does not exist'}

@patch('app.UserRepository')
def test_create_lobby__user_in_lobby(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user

    response = client.post('/create_lobby/?lobby_name=Lobby1&min_players=4&max_players=12&password=empty&host_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This user is already in a lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_create_lobby__lobby_already_exits(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/create_lobby/?lobby_name=Lobby1&min_players=4&max_players=12&password=empty&host_name=User1')
    assert response.status_code == 400
    assert response.json() == {'detail': 'This lobby name already exists'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_create_lobby__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = False
    mock_repository_lobby.create_lobby.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/create_lobby/?lobby_name=Lobby1&min_players=4&max_players=12&password=empty&host_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while creating the lobby'}

# Join lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_lobby_full.return_value = False
    mock_repository_lobby.is_password_correct.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 200
    assert response.json() == {'message': 'Joined lobby'}

@patch('app.UserRepository')
def test_join_lobby__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This user does not exist'}

@patch('app.UserRepository')
def test_join_lobby__user_in_lobby(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This user is already in a lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby__lobby_does_not_exist(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby__lobby_is_full(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_lobby_full.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This lobby is full'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby__password_is_wrong(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_lobby_full.return_value = False
    mock_repository_lobby.is_password_correct.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Incorrect password'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_lobby_full.return_value = False
    mock_repository_lobby.is_password_correct.return_value = True
    mock_repository_lobby.add_user_to_lobby.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while joining the lobby'}

# View lobby players tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users(mock_UserRepository, mock_LobbyRepository, lobby_players):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.get_lobby_users.return_value = lobby_players

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 200
    assert response.json() == lobby_players

@patch('app.UserRepository')
def test_get_lobby_users__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This user does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users__lobby_does_not_exist(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_lobby.lobby_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.get_lobby_users.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while getting the lobby users'}

# Start game tests
''' Work in progress
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
'''