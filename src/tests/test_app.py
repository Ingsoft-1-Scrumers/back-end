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
def lobby_users():
    return [{"name": "User1"} , {"name" : "User2"}, {"name" : "User3"}, {"name" : "User4"}, {"host": "User1"}]

@pytest.fixture
def lobby_positions():
    return [{'name': 'User1', 'position': 1}, {'name': 'User2', 'position': 2}, {'name': 'User3', 'position': 3}, {'name': 'User4', 'position': 4}]

@pytest.fixture
def user_hand():
    return [
  {
    "id": 4,
    "name": "Infectado",
    "type": "Contagio"
  },
  {
    "id": 25,
    "name": "Seduccion",
    "type": "Accion"
  },
  {
    "id": 3,
    "name": "Infectado",
    "type": "Contagio"
  },
  {
    "id": 5,
    "name": "Infectado",
    "type": "Contagio"
  }
]

@pytest.fixture
def card():
    return {
  "id": 55,
  "name": "Infectado",
  "type": "Contagio"
}

# Crear usuario tests
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

# Crear lobby tests
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

# Unirse a lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
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
def test_join_lobby__user_in_a_lobby(mock_UserRepository):
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
def test_join_lobby__game_already_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has already started'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_join_lobby__lobby_is_full(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
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
    mock_repository_lobby.is_game_started.return_value = False
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
    mock_repository_lobby.is_game_started.return_value = False
    mock_repository_lobby.is_lobby_full.return_value = False
    mock_repository_lobby.is_password_correct.return_value = True
    mock_repository_lobby.add_user_to_lobby.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/join_lobby/?lobby_name=Lobby1&user_name=User1&password=empty')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while joining the lobby'}

# Ver usuarios en lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users(mock_UserRepository, mock_LobbyRepository, lobby_users):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.get_lobby_users.return_value = lobby_users

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 200
    assert response.json() == lobby_users

@patch('app.LobbyRepository')
def test_get_lobby_users__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_lobby_users__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

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

    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.get_lobby_users.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while getting the lobby users'}

# Iniciar juego tests
@patch('app.GameLogic')
@patch('app.UserRepository')
@patch('app.LobbyRepository')
def test_start_game(mock_LobbyRepository, mock_UserRepository, mock_GameLogic):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = True
    mock_repository_user.is_user_host.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
    mock_repository_gamelogic.start_game.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 200
    assert response.json() == {'message': 'Game started successfully'}

@patch('app.LobbyRepository')
def test_start_game__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}


@patch('app.LobbyRepository')
def test_start_game__not_enough_players(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This lobby does not have enough players'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_start_game__user_not_host(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = True
    mock_repository_user.is_user_host.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not the host of the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_start_game__game_already_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = True
    mock_repository_user.is_user_host.return_value = True
    mock_repository_lobby.is_game_started.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has already started'}

@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_start_game__error(mock_UserRepository, mock_LobbyRepository, mock_GameLogic):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = True
    mock_repository_user.is_user_host.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
    mock_repository_gamelogic.start_game.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/start_game/?lobby_name=Lobby1&host_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while starting the game'}


@patch('app.LobbyRepository')
def test_is_lobby_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_lobby_exist/Lobby1')
    assert response.status_code == 200
    assert response.json() == {'exist': True}
     
    
# Ver si el juego ha empezado tests
@patch('app.LobbyRepository')
def test_is_game_started__game_started(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_game_started/Lobby1')
    assert response.status_code == 200
    assert response.json() == {'started' : True}

@patch('app.LobbyRepository')
def test_is_game_started__game_not_started(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_game_started/Lobby1')
    assert response.status_code == 200
    assert response.json() == {'started' : False}

@patch('app.LobbyRepository')
def test_is_game_started__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_game_started/Lobby1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
def test_is_game_started__error(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.side_effect = Exception()

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_game_started/Lobby1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while checking if the game is started'}

# Obtener posición de los usuarios tests
@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_users_position(mock_UserRepository, mock_LobbyRepository, mock_GameRepository, lobby_positions):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_game.get_users_position.return_value = lobby_positions

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    response = client.get('/get_users_position/Lobby1?user_name=User1')
    assert response.status_code == 200
    assert response.json() == lobby_positions

@patch('app.LobbyRepository')
def test_get_users_position__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_users_position/Lobby1?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_users_position__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_users_position/Lobby1?user_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_users_position__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_users_position/Lobby1?user_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has not started yet'}

@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_users_position__error(mock_UserRepository, mock_LobbyRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_game.get_users_position.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    response = client.get('/get_users_position/Lobby1?user_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while getting the users position'}

# Obtener mano de un usuario tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_user_hand(mock_UserRepository, mock_LobbyRepository, user_hand):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.get_user_hand.return_value = user_hand

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_user_hand/User1?lobby_name=User1')
    assert response.status_code == 200
    assert response.json() == user_hand

@patch('app.LobbyRepository')
def test_get_user_hand__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_user_hand/User1?lobby_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_user_hand__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_user_hand/User1?lobby_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_user_hand__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_user_hand/User1?lobby_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has not started yet'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_user_hand__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.get_user_hand.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/get_user_hand/User1?lobby_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while getting the hand'}

# Robar carta tests
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck(mock_UserRepository, mock_LobbyRepository, mock_GameLogic, card):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game_logic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 4
    mock_repository_game_logic.steal_card_from_deck.return_value = card

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_game_logic

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 200
    assert response.json() == card

@patch('app.LobbyRepository')
def test_steal_card_from_deck__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has not started yet'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__user_not_turn(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'It is not your turn'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__user_hand_is_full(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 5

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This user already has 5 cards'}

@patch('app.CardRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__error(mock_UserRepository, mock_LobbyRepository, mock_CardRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_card = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 4
    mock_repository_card.steal_card_from_deck.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_CardRepository.return_value = mock_repository_card

    response = client.get('/steal_card_from_deck/Lobby1?user_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while stealing a card'}

# Ver si es el turno de un usuario tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_is_user_turn__true(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 200
    assert response.json() == {'turn' : True}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_is_user_turn__false(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 200
    assert response.json() == {'turn' : False}

@patch('app.LobbyRepository')
def test_is_user_turn__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_is_user_turn__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_is_user_turn__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has not started yet'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_is_user_turn__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_turn.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_my_turn/User1?lobby_name=Lobby1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while checking if it is the user turn'}

# Jugar carta tests
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card(mock_UserRepository, mock_LobbyRepository, mock_GameLogic):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 5
    mock_repository_user.check_user_has_card.return_value = True
    mock_repository_gamelogic.play_card.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 200
    assert response.json() == {'message' : 'Card played successfully'}


@patch('app.LobbyRepository')
def test_play_card__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__target_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This target user is not in the lobby'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__target_not_alive(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This target user is not alive'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__user_not_turn(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = True
    mock_repository_user.is_user_turn.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'It is not your turn'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__user_hand_is_not_full(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 4

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This user does not have 5 cards'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__user_does_not_have_card(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 5
    mock_repository_user.check_user_has_card.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user does not have this card'}

@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__error(mock_UserRepository, mock_LobbyRepository, mock_GameLogic):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.is_target_alive.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_user.get_total_cards.return_value = 5
    mock_repository_user.check_user_has_card.return_value = True
    mock_repository_gamelogic.play_card.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/play_card/?lobby_name=Lobby1&user_name=User1&target_user_name=User2&id_card=1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while playing the card'}

# Finalizar juego tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
@patch('app.GameLogic')
def test_end_game(mock_GameLogic, mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_gamelogic.end_game.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/end_game/?lobby_name=Lobby1&user_name=User1')
    assert response.status_code == 200
    assert response.json() == {'message': 'Game ended successfully'}

@patch('app.LobbyRepository')
def test_end_game__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/end_game/?lobby_name=Lobby1&user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This lobby name does not exist'}

@patch('app.LobbyRepository')
def test_end_game__game_not_started(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/end_game/?lobby_name=Lobby1&user_name=User1')
    assert response.status_code == 406
    assert response.json() == {'detail': 'This game has not started yet'}

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_end_game__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.post('/end_game/?lobby_name=Lobby1&user_name=User1')
    assert response.status_code == 401
    assert response.json() == {'detail': 'This user is not in the lobby'}

@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_end_game__error(mock_UserRepository, mock_LobbyRepository, mock_GameLogic):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_gamelogic.end_game.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    response = client.post('/end_game/?lobby_name=Lobby1&user_name=User1')
    assert response.status_code == 500
    assert response.json() == {'detail': 'An error occurred while ending the game'}