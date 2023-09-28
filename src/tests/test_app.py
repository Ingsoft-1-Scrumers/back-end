import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app import app

client = TestClient(app)


@pytest.fixture
def user_a():
    return {"name": "Miguel"}


@patch('app.UserRepository')
def test_create_user(mock_UserRepository, user_a):
    mock_repository = MagicMock()
    mock_repository.create_user.return_value = user_a
    mock_UserRepository.return_value = mock_repository

    response = client.post("/create_user/?user_name=Miguel")
    assert response.status_code == 200
    assert response.json() == {'message': 'User created'}


