import requests
import pytest

SERVICE_URL = "http://localhost:8000"


@pytest.fixture
def list_of_users():
    return [
        {'name': 'User_1'},
        {'name': 'User_2'},
        {'name': 'User_3'},
        {'name': 'User_4'},
        {'host': 'User_2'}
    ]


@pytest.mark.end2end_test
def test_get_lobby_users_end_point(list_of_users):
    data = requests.get(f"{SERVICE_URL}/lobby_users/1234_lobby?user_name=User_2")
    #la respuesta viene desordenada ya que obtiene de un set, entonces ordenamos antes de comparar
    #clasificamos en nivel de prioridad, primero los que tienen name y luego los que tienen host
    sorted_data = sorted(data.json(), key=lambda x: (0 if 'name' in x else 1, x.get('name', '')))
    assert sorted_data == list_of_users
