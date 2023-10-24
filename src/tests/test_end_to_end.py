import requests
import pytest

SERVICE_URL = "http://localhost:8000"

@pytest.fixture
def list_of_users():
    return [
        {'host': 'User_2'},
        {'name': 'User_1'},
        {'name': 'User_2'},
        {'name': 'User_3'},
        {'name': 'User_4'}
    ]

@pytest.mark.end2end_test
def test_get_lobby_users_end_point(list_of_users):
    data = requests.get(f"{SERVICE_URL}/lobby_users/1234_lobby")
    #la respuesta viene desordenada ya que obtiene de un set, entonces ordenamos antes de comparar
    #clasificamos en nivel de prioridad, primero los que tienen name y luego los que tienen host
    sorted_data = data.json()
    assert sorted_data == list_of_users, "The list of users in the lobby is not correct"