import pytest
from pony.orm import count, db_session

from user_repository import UserRepository
from models import User


@pytest.fixture
def user_repository():
    return UserRepository()

"""
@pytest.mark.integration_test
@db_session
def test_get_products(user_repository: UserRepository):
    list_of_products = user_repository.get_products()
    assert len(list_of_products) == count(User.select())
"""

"""
Prubea de integración:
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
