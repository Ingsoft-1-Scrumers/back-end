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
def joinable_lobbies():
    return [{'name': 'string', 'min_players': 0, 'total_players': 1, 'max_players': 0, 'secure': True}, {'name': 'lol', 'min_players': 0, 'total_players': 1, 'max_players': 0, 'secure': True}]

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

#combinations es un diccionario con los objetivos de cada carta
@pytest.fixture
def combinations():
    return [
    {"card_id": 1,
    "valid": ["user2", "user3"],
    "discard": True},
    {"card_id": 2,
    "valid": ["user1", "user3"],
    "discard": False},
    {"card_id": 3,
    "valid": ["user1", "user2"],
    "discard": False},
    {"card_id": 4,
    "valid": ["user1", "user2", "user3"],
    "discard": False},
    ]

@pytest.fixture
def role():
    return "Infectado"

def assert_response_equals(response, expected_status_code, expected_json):
    assert response.status_code == expected_status_code, f"Expected status code {expected_status_code}, but got {response.status_code}."
    assert response.json() == expected_json, f"Expected JSON {expected_json}, but got {response.json()}."


# Crear usuario tests
@patch('app.UserRepository')
def test_create_user(mock_UserRepository, user):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository

    response = client.post(url="/create_user/", json={"user_name": "User1"})
    assert_response_equals(response, 200, {'message': 'User created'})


@patch('app.UserRepository')
def test_create_user_user_already_exists(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = True

    mock_UserRepository.return_value = mock_repository

    response = client.post(url="/create_user/", json={"user_name": "User1"})
    assert_response_equals(response, 400, {'detail': 'This username already exists'})

@patch('app.UserRepository')
def test_create_user__error(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = False
    mock_repository.create_user.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository

    response = client.post(url="/create_user/", json={"user_name": "User1"})
    assert_response_equals(response, 500, {'detail': 'An error occurred while creating the user'})

# Existe usuario tests
@patch('app.UserRepository')
def test_is_user_exist(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = True

    mock_UserRepository.return_value = mock_repository

    response = client.get('/is_user_exist/User1')
    assert_response_equals(response, 200, {'exist': True})

@patch('app.UserRepository')
def test_is_user_exist__user_does_not_exist(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository

    response = client.get('/is_user_exist/User1')
    assert_response_equals(response, 200, {'exist': False})

@patch('app.UserRepository')
def test_is_user_exist__error(mock_UserRepository):
    mock_repository = MagicMock()

    mock_repository.user_exists.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository

    response = client.get('/is_user_exist/User1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while checking if user exist'})

# Crear lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_create_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    
    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = False
    mock_repository_lobby.lobby_exists.return_value = False
    mock_repository_lobby.create_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}
    response = client.post(url='/create_lobby/', json=json_body)
    assert_response_equals(response, 200, {'message': 'Lobby created'})


@patch('app.UserRepository')
def test_create_lobby__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    json_body = {"lobby_name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}
    response = client.post(url='/create_lobby/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This user does not exist'})

@patch('app.UserRepository')
def test_create_lobby__user_in_lobby(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user

    json_body = {"lobby_name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}
    response = client.post(url='/create_lobby/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This user is already in a lobby'})

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

    json_body = {"lobby_name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}
    response = client.post(url='/create_lobby/', json=json_body)
    assert_response_equals(response, 400, {'detail': 'This lobby name already exists'})

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

    json_body = {"lobby_name": "Lobby1", "min_players": 4, "max_players": 12, "password": "empty", "host_name": "User1"}
    response = client.post(url='/create_lobby/', json=json_body)
    assert_response_equals(response, 500, {'detail': 'An error occurred while creating the lobby'})

# Existe lobby tests
@patch('app.LobbyRepository')
def test_is_lobby_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_lobby_exist/Lobby1')
    assert_response_equals(response, 200, {'exist': True})

@patch('app.LobbyRepository')
def test_is_lobby_exist__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_lobby_exist/Lobby1')
    assert_response_equals(response, 200, {'exist': False})

@patch('app.LobbyRepository')
def test_is_lobby_exist__error(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.side_effect = Exception()

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/is_lobby_exist/Lobby1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while checking if lobby exist'})

# Obtener lista de lobbies tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_joinable_lobbies(mock_UserRepository, mock_LobbyRepository, joinable_lobbies):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_lobby.get_joinable_lobby_listings.return_value = joinable_lobbies

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/joinable_lobbies/?user_name=User1')
    assert_response_equals(response, 200, joinable_lobbies)


'''ELIMINAR ya no exigimos user_name en el body

@patch('app.UserRepository')
def test_joinable_lobbies__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    response = client.get('/joinable_lobbies/?user_name=User1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'This user does not exist'}
'''

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_joinable_lobbies__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_lobby.get_joinable_lobby_listings.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/joinable_lobbies/?user_name=User1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while getting the joinable lobbies'})

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
    mock_repository_lobby.add_user_to_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 200, {'message': 'Joined lobby'})


@patch('app.UserRepository')
def test_join_lobby__user_does_not_exist(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = False

    mock_UserRepository.return_value = mock_repository_user

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This user does not exist'})

@patch('app.UserRepository')
def test_join_lobby__user_in_a_lobby(mock_UserRepository):
    mock_repository_user = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_user.is_user_in_a_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This user is already in a lobby'})

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

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

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

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This game has already started'})

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

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This lobby is full'})

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

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'Incorrect password'})

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

    json_body = {"lobby_name": "Lobby1", "password": "empty", "user_name": "User1"}
    response = client.post(url='/join_lobby/', json=json_body)
    assert_response_equals(response, 500, {'detail': 'An error occurred while joining the lobby'})

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
    assert_response_equals(response, 200, lobby_users)

@patch('app.LobbyRepository')
def test_get_lobby_users__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1?user_name=User1')
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})


@patch('app.LobbyRepository')
def test_get_lobby_users__error(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.get_lobby_users.side_effect = Exception()

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get('/lobby_users/Lobby1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while getting the lobby users'})

# Abandonar lobby tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_leave_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_lobby = MagicMock()
    mock_repository_user = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post('/leave_lobby/', json=json_body)
    assert_response_equals(response, 200, {'message': 'User left lobby successfully'})

@patch('app.LobbyRepository')
def test_leave_lobby__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post('/leave_lobby/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_leave_lobby__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post('/leave_lobby/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'This user is not in the lobby'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_leave_lobby__game_already_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post('/leave_lobby/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This game has already started'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_leave_lobby__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
    mock_repository_lobby.leave_lobby.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post('/leave_lobby/', json=json_body)
    assert_response_equals(response, 500, {'detail': 'An error occurred while leaving the lobby'})

# Iniciar juego tests
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_start_game(mock_UserRepository, mock_LobbyRepository, mock_GameLogic):
    mock_repository_lobby = MagicMock()
    mock_repository_user = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = True
    mock_repository_user.is_user_host.return_value = True
    mock_repository_lobby.is_game_started.return_value = False
    mock_repository_gamelogic.start_game.return_value = True

    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_UserRepository.return_value = mock_repository_user
    mock_GameLogic.return_value = mock_repository_gamelogic

    json_body = {"lobby_name": "Lobby2", "user_name": "User2"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 200, {'message': 'Game started'})

@patch('app.LobbyRepository')
def test_start_game__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
def test_start_game__not_enough_players(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.can_start_game.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This lobby does not have enough players'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'This user is not the host of the lobby'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This game has already started'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/start_game/', json=json_body)
    assert_response_equals(response, 500, {'detail': 'An error occurred while starting the game'})

#chequea que todos los usuarios esten listos
@patch('app.UserRepository')
@patch('app.LobbyRepository')
def test_is_set_user_ready(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/ready/', json=json_body)
    assert response.status_code == 200, response.json()

# Obtener posición de los usuarios tests
@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_users_position(mock_UserRepository, mock_LobbyRepository, mock_GameRepository, lobby_positions):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_game.get_users_position.return_value = lobby_positions

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    response = client.get(url='/users_position/Lobby1')
    assert_response_equals(response, 200, lobby_positions)

@patch('app.LobbyRepository')
def test_users_position__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/users_position/Lobby1')
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_users_position__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/users_position/Lobby1')
    assert_response_equals(response, 406, {'detail': 'This game has not started yet'})

@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_users_position__error(mock_UserRepository, mock_LobbyRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_game.get_users_position.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    response = client.get(url='/users_position/Lobby1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while getting the users position'})

# Obtener mano de un usuario tests
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_user_hand(mock_UserRepository, mock_LobbyRepository, user_hand):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.get_user_hand.return_value = user_hand

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/user_hand/Lobby1/User1')
    assert_response_equals(response, 200, user_hand)

@patch('app.LobbyRepository')
def test_user_hand__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/user_hand/Lobby1/User1')
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_user_hand__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/user_hand/Lobby1/User1')
    assert_response_equals(response, 401, {'detail': 'This user is not in the lobby'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_user_hand__game_not_started(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/user_hand/Lobby1/User1')
    assert_response_equals(response, 406, {'detail': 'This game has not started yet'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_user_hand__error(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.get_user_hand.side_effect = Exception()

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    response = client.get(url='/user_hand/Lobby1/User1')
    assert_response_equals(response, 500, {'detail': 'An error occurred while getting the hand'})

# Obtener objetivos de la carta
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_play_combinations(mock_UserRepository, mock_LobbyRepository, mock_GameLogic, combinations):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game_logic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_game_logic.get_play_combinations.return_value = combinations

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_game_logic

    response = client.get(url='/user_cards_info/Lobby1/User1')
    assert response.status_code == 200, response.json()
    assert response.json() == combinations, response.json()

# Robar carta tests
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
@patch('app.GameRepository')
def test_steal_card(mock_UserRepository, mock_LobbyRepository, mock_GameLogic,mock_GameRepository ,card):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game_logic = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_lobby.game_repo.get_game_status.return_value = 'steal_card_stage'

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_game_logic
    mock_GameRepository.return_value = mock_repository_game
    
    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/steal_card/', json=json_body)
    assert response.status_code == 200

@patch('app.LobbyRepository')
def test_steal_card_from_deck__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/steal_card/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_steal_card_from_deck__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/steal_card/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'This user is not in the lobby'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/steal_card/', json=json_body)
    assert_response_equals(response, 406, {'detail': 'This game has not started yet'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1"}
    response = client.post(url='/steal_card/', json=json_body)
    assert_response_equals(response, 500, {'detail': 'An error occurred while stealing a card'})

# Descartar carta
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
@patch('app.CardRepository')
@patch('app.GameRepository')
def test_discard_card(mock_UserRepository, mock_LobbyRepository, mock_GameLogic, mock_CardRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.check_user_has_card.return_value = True
    mock_repository_user.is_user_turn.return_value = True
    mock_repository_gamelogic.can_card_be_discarded.return_value = True
    mock_repository_gamelogic.discard_card.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2","card_id": 1}
    response = client.post(url='/discard_card/', json=json_body)
    assert response.status_code == 200

# Jugar carta tests
@patch('app.GameLogic')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
@patch('app.CardRepository')
@patch('app.GameRepository')
def test_play_card(mock_UserRepository, mock_LobbyRepository, mock_GameLogic, mock_CardRepository, mock_GameRepository):
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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/play_card/', json=json_body)
    assert response.status_code == 200

@patch('app.LobbyRepository')
def test_play_card__lobby_does_not_exist(mock_LobbyRepository):
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = False

    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/play_card/', json=json_body)
    assert_response_equals(response, 404, {'detail': 'This lobby name does not exist'})

@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_play_card__user_not_in_lobby(mock_UserRepository, mock_LobbyRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = False

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/play_card/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'This user is not in the lobby'})


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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/play_card/', json=json_body)
    assert_response_equals(response, 401, {'detail': 'This user does not have this card'})

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

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/play_card/', json=json_body)
    assert_response_equals(response, 500, {'detail':'An error occurred while playing the card'})

@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_defend_or_skip(mock_UserRepository, mock_LobbyRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "choice": "defense"}
    response = client.post(url='/defend_or_skip/', json=json_body)

    assert response.status_code == 200


@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_defend_or_exchange(mock_UserRepository, mock_LobbyRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "choice": "exchange"}
    response = client.post(url='/defend_or_exchange/', json=json_body)

    assert response.status_code == 200

@patch('app.UserRepository')
@patch('app.LobbyRepository')
@patch('app.GameLogic')
@patch('app.CardRepository')
@patch('app.GameRepository')
def test_defense_card(mock_GameLogic, mock_UserRepository, mock_LobbyRepository, mock_CardRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()
    mock_repository_card = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_card.get_card_name.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.check_user_has_card.return_value = True
    mock_repository_gamelogic.can_card_cancel_effect.return_value = True
    mock_repository_game.set_effect_to_be_applied.return_value = True
    mock_repository_gamelogic.discard_card.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic
    mock_CardRepository.return_value = mock_repository_card
    mock_GameRepository.return_value = mock_repository_game

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "card_id": 1}
    response = client.post(url='/defense_card/', json=json_body)

    assert response.status_code == 200


@patch('app.UserRepository')
@patch('app.LobbyRepository')
@patch('app.GameLogic')
@patch('app.CardRepository')
@patch('app.GameRepository')
def test_swap_card(mock_GameLogic, mock_UserRepository, mock_LobbyRepository, mock_CardRepository, mock_GameRepository):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_gamelogic = MagicMock()
    mock_repository_card = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_card.get_card_name.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_user.is_target_in_lobby.return_value = True
    mock_repository_user.check_user_has_card.return_value = True
    mock_repository_gamelogic.validate_swap_card.return_value = True
    mock_repository_game.is_there_exchange_offer.return_value = True
    mock_repository_game.set_exchange_card_finish.return_value = True
    mock_repository_game.get_exchange_user_start.return_value = True
    mock_repository_game.get_exchange_user_finish.return_value = True
    mock_repository_game.get_exchange_card_user_start.return_value = True
    mock_repository_game.get_exchange_card_user_finish.return_value = True
    mock_repository_user.is_user_in_quarantine.return_value = True
    mock_repository_user.is_user_in_quarantine.return_value = True
    mock_repository_card.get_card_dict.return_value = True
    mock_repository_game.set_effect_to_be_applied.return_value = True

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameLogic.return_value = mock_repository_gamelogic
    mock_CardRepository.return_value = mock_repository_card
    mock_GameRepository.return_value = mock_repository_game

    json_body = {"lobby_name": "Lobby1", "user_name": "User1", "target_user_name": "User2", "card_id": 1}
    response = client.post(url='/swap_card/', json=json_body)

    assert response.status_code == 200

@patch('app.GameRepository')
@patch('app.LobbyRepository')
@patch('app.UserRepository')
def test_get_user_role(mock_UserRepository, mock_LobbyRepository, mock_GameRepository, role):
    mock_repository_user = MagicMock()
    mock_repository_lobby = MagicMock()
    mock_repository_game = MagicMock()

    mock_repository_user.user_exists.return_value = True
    mock_repository_lobby.lobby_exists.return_value = True
    mock_repository_user.is_user_in_lobby.return_value = True
    mock_repository_lobby.is_game_started.return_value = True
    mock_repository_user.get_role.return_value = role

    mock_UserRepository.return_value = mock_repository_user
    mock_LobbyRepository.return_value = mock_repository_lobby
    mock_GameRepository.return_value = mock_repository_game

    response = client.get(url='/get_user_role/Lobby1/User1')
    assert_response_equals(response, 200, {'role': role})