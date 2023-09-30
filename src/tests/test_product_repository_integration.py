import pytest
from pony.orm import count, db_session

from models import User
from repository import UserRepository

@pytest.fixture
def user_repository():
    return UserRepository()

"""
Prueba de integracion:
Insertar un nuevo producto en la base de datos y aumentar la cantidad total de usuarios en uno
"""

@pytest.mark.integration_test
def test_create_user(user_repository: UserRepository):

    with db_session:
        N_users = count(User.select()) #N_user = cantidad actual de usuarios en la base de datos

    user_repository.create_user('User_N')

    with db_session:
        assert count(User.select()) == N_users + 1
        #Compara la cantidad de users en la base de datos después de crear el nuevo user con el valor almacenado en N_users más uno.