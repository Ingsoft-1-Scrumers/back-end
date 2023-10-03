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
    
    if lobby_repo.is_game_started(lobby_name):
        raise HTTPException(status_code=406, detail='This game has already started')

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

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.can_start_game(lobby_name)):
        raise HTTPException(status_code=406, detail='This lobby does not have enough players')
    
    if not (user_repo.is_user_host(lobby_name, host_name)):
        raise HTTPException(status_code=401, detail='This user is not the host of the lobby')
    
    if (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has already started')

    try:
        game_logic.start_game(lobby_name)
        return {'message': 'Game started successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while starting the game')

@app.get('/is_lobby_exist/{lobby_name}')
async def is_lobby_exist(lobby_name: str):
    lobby_repo = LobbyRepository()
    
    try:
        result = lobby_repo.lobby_exists(lobby_name)
        return {'exist': result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if lobby exist')
    

# Endpoints para obtener información del juego
@app.get('/is_game_started/{lobby_name}')
async def is_game_started(lobby_name: str):
    lobby_repo = LobbyRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    try:
        result = lobby_repo.is_game_started(lobby_name)
        return {'started': result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if the game is started')

@app.get('/get_users_position/{lobby_name}')
async def get_users_position(lobby_name: str, user_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()
    game_repo = GameRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
  
    try:
        return game_repo.get_users_position(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the users position')
    
@app.get('/get_user_hand/{user_name}') 
async def get_user_hand(lobby_name: str, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()  
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    try:
        return user_repo.get_user_hand(user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the hand')

@app.get('/steal_card_from_deck/{lobby_name}') 
async def steal_card_from_deck(lobby_name: str, user_name: str):
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    # En esta sprint solo se puede robar cartas en tu turno
    if not (user_repo.is_user_turn(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='It is not your turn')
    
    # En esta sprint solo se puede robar una carta si tienes menos de 5
    if (user_repo.get_total_cards(user_name) >= 5):
        raise HTTPException(status_code=406, detail='This user already has 5 cards')
    
    try:
        return game_logic.steal_card_from_deck(user_name) #! Esto deberia estar en el game_logic
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')

@app.get('/is_my_turn/{user_name}')
async def is_my_turn(lobby_name: str, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    try:
        result = user_repo.is_user_turn(lobby_name, user_name) 
        return {'turn': result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if it is the user turn')

@app.post('/play_card/')
async def play_card(lobby_name: str, user_name: str, target_user_name: str, id_card: int):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (user_repo.is_target_in_lobby(lobby_name, target_user_name)): 
        raise HTTPException(status_code=401, detail='This target user is not in the lobby')
    
    if not (user_repo.is_target_alive(target_user_name)):
        raise HTTPException(status_code=401, detail='This target user is not alive')
    
    # En esta sprint solo se puede jugar cartas en tu turno (no hay cartas de defensa)
    if not (user_repo.is_user_turn(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='It is not your turn')
    
    # En esta sprint solo se puede jugar una carta si se tienen 5
    if (user_repo.get_total_cards(user_name) < 5):
        raise HTTPException(status_code=406, detail='This user does not have 5 cards')

    if not (user_repo.check_user_has_card(user_name, id_card)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    try:
        game_logic.play_card(user_name, id_card, lobby_name)
        return  {'message': 'Card played successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while playing the card')

@app.post('/end_game/')
async def end_game(lobby_name: str, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
     
    try:
        game_logic.end_game(lobby_name)
        return  {'message': 'Game ended successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while ending the game')