from fastapi import FastAPI, HTTPException
from user_repository import UserRepository
from lobby_repository import LobbyRepository

app = FastAPI()

@app.post('/create_user/')
async def create_user(user_name: str):
    user_repo = UserRepository()
    
    if user_repo.user_exists(user_name):
        raise HTTPException(status_code=400, detail='This username already exists')
    
    try:
        user_repo.create_user(user_name)
        return {'message': 'User created'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while creating the user')

@app.post('/create_lobby/')
async def create_lobby(lobby_name: str, min_players: int, max_players: int, password: str, host_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()

    if not (user_repo.user_exists(host_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if user_repo.is_user_in_a_lobby(host_name):
        raise HTTPException(status_code=406, detail='This user is already in a lobby')

    if lobby_repo.lobby_exists(lobby_name):
        raise HTTPException(status_code=400, detail='This lobby name already exists')
    
    try:
        lobby_repo.create_lobby(lobby_name, min_players, max_players, password, host_name)
        return {'message': 'Lobby created'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while creating the lobby')
        
@app.post('/join_lobby/')
async def join_lobby(lobby_name: str, user_name: str, password: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if user_repo.is_user_in_a_lobby(user_name):
        raise HTTPException(status_code=406, detail='This user is already in a lobby')

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if lobby_repo.is_lobby_full(lobby_name):
        raise HTTPException(status_code=406, detail='This lobby is full')
    
    if not (lobby_repo.is_password_correct(lobby_name, password)):
        raise HTTPException(status_code=401, detail='Incorrect password')
    
    try:
        lobby_repo.add_user_to_lobby(lobby_name, user_name)
        return {'message': 'Joined lobby'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while joining the lobby')
    
@app.get('/lobby_users/{lobby_name}')
async def get_lobby(lobby_name: str, user_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        return lobby_repo.get_lobby_users(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the lobby users')
    