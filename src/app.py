from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from repository import *
from util import *

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def get_lobby_users(lobby_name: str, user_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        return lobby_repo.get_lobby_users(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the lobby users')

@app.post('/start_game/')
async def start_game(lobby_name: str, host_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()

    if not (user_repo.user_exists(host_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, host_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.can_start_game(lobby_name)):
        raise HTTPException(status_code=406, detail='This lobby does not have enough players')
    
    if not (user_repo.is_user_host(lobby_name, host_name)):
        raise HTTPException(status_code=401, detail='This user is not the host of the lobby')
    
    try:
        game_logic.start_game(lobby_name)
        return {'message': 'Game started successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while starting the game')

# Endpoints para obtener información del juego
@app.get('/is_game_started/{lobby_name}')
async def is_game_started(lobby_name: str):
    lobby_repo = LobbyRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    try:
        if lobby_repo.is_game_started(lobby_name):
            return {'message': 'Game has started'}
        else:
            return {'message': 'Game has not started'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if the game is started')

@app.get('/get_users_position/{lobby_name}')
async def get_users_position(lobby_name: str, user_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()
    game_repo = GameRepository()
    
    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        game = lobby_repo.get_game(lobby_name)
        return game_repo.get_users_positions(game)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the users position')

'''
@app.get('/get_user_hand/{user_name}')
async def get_user_hand(user_name: str):
    user_repo = UserRepository()  

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        return user_repo.get_user_hand(user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the hand')


@app.get('/')
async def steal_card_from_deck(user_name: str):
    card_repo = CardRepository()
    user_repo = UserRepository()
    
    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        return card_repo.steal_card_from_deck(user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')
'''