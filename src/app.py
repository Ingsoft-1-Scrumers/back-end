from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from connection import ConnectionManager
from repository import *
from util import *
from basemodels import *

app = FastAPI()
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/lobby_listing/")
async def get_lobby_listing(UserWSRequest: UserWSRequest):
    websocket = UserWSRequest.websocket
    user_name = UserWSRequest.user_name
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    await manager.user_connect(websocket, user_name)
    joinable_lobbies = lobby_repo.get_joinable_lobby_listings()
    await manager.send_message_to_user(user_name, joinable_lobbies)
    try:
        while True:
            await manager.user_connection_sleep(user_name)
    except WebSocketDisconnect: #! Aca se puede hacer la logica para una desconexión no esperada
        manager.user_disconnet(user_name)

@app.websocket("/lobby/{lobby_name}")
async def get_lobby_status(LobbyWSRequest: LobbyWSRequest):
    websocket = LobbyWSRequest.websocket
    lobby_name = LobbyWSRequest.lobby_name
    user_name = LobbyWSRequest.user_name
    lobby_repo = LobbyRepository()
    user_repo = UserRepository()

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    await manager.lobby_user_connect(websocket, lobby_name, user_name)
    user_dict = lobby_repo.get_lobby_users(lobby_name)
    await manager.broadcast_to_lobby(lobby_name, f"Users: {user_dict}")
    try:
        while True:
            message = await manager.receive_message_from_lobby_user(lobby_name, user_name)
            await manager.broadcast_to_lobby(lobby_name, f"Message: {user_name}: {message}")
    except WebSocketDisconnect: #! Aca se puede hacer la logica para una desconexión no esperada
        manager.lobby_user_disconnect(lobby_name, user_name)
        user_dict = lobby_repo.get_lobby_users(lobby_name)
        await manager.broadcast_to_lobby(lobby_name, f"Message: Server: {user_name} has left the lobby")
        await manager.broadcast_to_lobby(lobby_name, f"Users: {user_dict}")

@app.post('/create_user/')
async def create_user(new_user: CreateUserRequest):
    user_name = new_user.user_name
    user_repo = UserRepository()
    
    if user_repo.user_exists(user_name):
        raise HTTPException(status_code=400, detail='This username already exists')
    
    try:
        user_repo.create_user(user_name)
        return {'message': 'User created'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while creating the user')
    
@app.get('/is_user_exist/{user_name}')
async def is_user_exist(user_name: str):
    user_repo = UserRepository()
    
    try:
        result = user_repo.user_exists(user_name)
        return {'exist': result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if user exist')

@app.post('/create_lobby/')
async def create_lobby(new_lobby: CreateLobbyRequest):
    lobby_name = new_lobby.lobby_name
    min_players = new_lobby.min_players
    max_players = new_lobby.max_players
    password = new_lobby.password
    host_name = new_lobby.host_name
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
        joinable_lobbies = lobby_repo.get_joinable_lobby_listings()
        await manager.broadcast_to_users(joinable_lobbies)
        return {'message': 'Lobby created'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while creating the lobby')
    
@app.get('/is_lobby_exist/{lobby_name}')
async def is_lobby_exist(lobby_name: str):
    lobby_repo = LobbyRepository()
    
    try:
        result = lobby_repo.lobby_exists(lobby_name)
        return {'exist': result}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while checking if lobby exist')

@app.post('/join_lobby/')
async def join_lobby(request: JoinLobbyRequest):
    lobby_name = request.lobby_name
    password = request.password
    user_name = request.user_name
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
        user_dict = lobby_repo.get_lobby_users(lobby_name)
        joinable_lobbies = lobby_repo.get_joinable_lobby_listings()
        await manager.broadcast_to_lobby(lobby_name, f"Users: {user_dict}")
        await manager.broadcast_to_users(joinable_lobbies)
        return {'message': 'Joined lobby'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while joining the lobby')

@app.post('/start_game/')
async def start_game(request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.can_start_game(lobby_name)):
        raise HTTPException(status_code=406, detail='This lobby does not have enough players')
    
    if not (user_repo.is_user_host(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not the host of the lobby')
    
    if (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has already started')

    try:
        game_logic.start_game(lobby_name)
        joinable_lobbies = lobby_repo.get_joinable_lobby_listings()
        await manager.broadcast_to_lobby(lobby_name, 'Notification: The game has started')
        await manager.broadcast_to_users(joinable_lobbies)
        return {'message': 'Game started successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while starting the game')
 
# Endpoints para obtener información del juego

#! VA EN WEB SOCKET
@app.get('/get_users_position/{lobby_name}')
async def get_users_position(request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
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

@app.get('/get_user_hand/{user}') 
async def get_user_hand(user: str, request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
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
async def steal_card_from_deck(request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
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
        return game_logic.steal_card_from_deck(user_name) 
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')

#! VA EN WEB SOCKET
@app.get('/is_my_turn/{user_name}')
async def is_my_turn(request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
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
async def play_card(request: PlayCardRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
    target_user_name = request.target_user_name
    card_id = request.card_id
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

    if not (user_repo.check_user_has_card(user_name, card_id)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    try:
        game_logic.play_card(user_name, card_id, lobby_name)
        return  {'message': 'Card played successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while playing the card')

@app.post('/end_game/')
async def end_game(request: LobbyUserRequest):
    lobby_name = request.lobby_name
    user_name = request.user_name
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