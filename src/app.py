#branch refactor

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

async def game_flow(lobby_name : str): 
    game_repo = GameRepository()
    game_logic = GameLogic()
    game_status = game_repo.get_game_status(lobby_name)
    user_turn = game_repo.get_turn_user(lobby_name)

    match game_status:
        case 'game_not_started':
            game_repo.set_game_status(lobby_name, "steal_card_stage_user_turn")
            await manager.broadcast_to_lobby_users(lobby_name, f"turn, {user_turn}")
            await manager.send_message(user_turn, f"steal_card_stage_user_turn, {user_turn}")
        case 'steal_card_stage_user_turn':
            if (game_logic.can_user_play(user_turn, lobby_name)):
                game_repo.set_game_status(lobby_name, "discard_or_play_user_turn")
                await manager.send_message(user_turn, f"discard_or_play_user_turn, {user_turn}")
            else:
                game_repo.set_game_status(lobby_name, "discard_card_stage_user_turn") 
                await manager.send_message(user_turn, f"discard_card_stage_user_turn, {user_turn}")

        case 'discard_or_play_user_turn':
            if (game_repo.get_discard_or_play(lobby_name) == 'discard'):
                game_repo.set_game_status(lobby_name, "discard_card_stage_user_turn")
                await manager.send_message(user_turn, f"discard_card_stage_user_turn, {user_turn}")
            else:
                game_repo.set_game_status(lobby_name, "play_card_stage_user_turn")
                await manager.send_message(user_turn, f"play_card_stage_user_turn, {user_turn}")

        case 'discard_card_stage_user_turn':
            user_next_turn = game_logic.next_player(lobby_name)
            superinfection = game_logic.exchange_with_superinfection(user_turn, user_next_turn)
            obstacle = game_logic.is_there_obstacle(lobby_name, user_next_turn)

            if (superinfection) or (obstacle): # No hay intercamio de cartas
                game_repo.set_game_status(lobby_name, "steal_card_stage_user_turn")
                await manager.send_message(user_turn, f"no_exchange, {user_turn}")
                game_logic.next_turn(lobby_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"turn, {user_next_turn}")
                await manager.send_message(user_next_turn, f"steal_card_stage_user_turn, {user_next_turn}")
            else: # Hay intercambio de cartas
                game_repo.set_game_status(lobby_name, "exchange_card_start")
                await manager.send_message(user_turn, f"exchange_card_start, {user_turn}, {user_next_turn}")
                
        case 'play_card_stage_user_turn':
            #! Falta campo objetivo en game
            await manager.send_message(user_turn, f"waiting_for_exchange, {user_turn}, {user_finish}")
            
            
            #checkear si hay defensa o no (Barbacoa o Cambio de lugar)
            if (not defense):
                #aplicar efecto de carta

            else:
                #preguntar si quiere defenderse o no
                await manager.send_message(target_user_name, f"defense_or_suffer, {target_user_name}, {user_turn}")
                game_repo.set_game_status(lobby_name, "defense_or_suffer")

        case 'exchange_card_start':
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            await manager.send_message(user_turn, f"waiting_for_exchange, {user_turn}, {user_finish}")

            if (game_logic.can_user_defend_exchange(user_finish)): # Se puede defender
                game_repo.set_game_status(lobby_name, "defense_or_exchange")
                await manager.send_message(user_finish, f"defense_or_exchange, {user_finish}, {user_turn}")
            else: # No se puede defender
                game_repo.set_game_status(lobby_name, "exchange_card_finish")
                await manager.send_message(user_next_turn, f"exchange_card_finish, {user_finish}, {user_turn}")
                
        case 'exchange_card_finish':
            victory = False
            if (victory):
                await manager.broadcast_to_lobby_users(lobby_name, f"game_over, {user_turn}")
                # Mostrar pantalla de victoria
                # Borrar todo
                # Cerrar el lobby socket
            else:
                game_repo.set_game_status(lobby_name, "steal_card_stage_user_turn")
                game_logic.next_turn(lobby_name)
                user_next_turn = game_repo.get_turn_user(lobby_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"turn, {user_next_turn}")
                await manager.send_message(user_next_turn, f"steal_card_stage_user_turn, {user_next_turn}")

        case 'unexpected_disconnection':
            # Borrar todo
            # Cerrar el lobby socket
 
#! Asumimos que el usuario solo cierra pestaña cuando no esta en un lobby/partida
@app.websocket('/websocket/{user_name}')
async def lobby_listing(websocket: WebSocket, user_name: str):
    user_repo = UserRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    await manager.connect(websocket, user_name)
    try:
        while True:
            message = await manager.receive_message(user_name)
            lobby_name = user_repo.get_user_lobby(user_name)

            if (lobby_name is not None):
                await manager.broadcast_to_lobby_users(lobby_name, f"chat_msg, {user_name}, {message}")
            else:
                raise HTTPException(status_code=401, detail='This user is not in a lobby')
            
    except WebSocketDisconnect: #! Logica para desconexion no esperada
        await manager.disconnect(user_name) 
           
@app.post('/create_user/')
async def create_user(user: UserBase):
    user_name = user.user_name
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
async def create_lobby(lobby: CreateLobbyBase):
    lobby_name = lobby.lobby_name
    min_players = lobby.min_players
    max_players = lobby.max_players
    password = lobby.password
    host_name = lobby.host_name
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
        total_users = lobby_repo.get_amount_users(lobby_name)
        is_private = lobby_repo.is_lobby_private(lobby_name)
        await manager.add_user_to_lobby(lobby_name, host_name)
        await manager.broadcast_to_users_with_no_lobby(f"new_lobby, {lobby_name}, {total_users}, {max_players}, {is_private}")
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

@app.get('/joinable_lobbies/')
async def get_joinable_lobbies(user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()

    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    try:
        joinable_lobbies = lobby_repo.get_joinable_lobby_listings()
        return joinable_lobbies
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the joinable lobbies')

@app.post('/join_lobby/')
async def join_lobby(request: JoinLobbyBase):
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
        total_users = lobby_repo.get_amount_users(lobby_name)
        await manager.broadcast_to_lobby_users(lobby_name, f"user_connect, {user_name}")
        await manager.add_user_to_lobby(lobby_name, user_name)
        await manager.broadcast_to_users_with_no_lobby(f"update_players, {lobby_name}, {total_users}")
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

@app.post('/leave_lobby/')
async def leave_lobby(request: LobbyBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')

    if (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has already started')
    
    try:
        lobby_repo.leave_lobby(lobby_name, user_name)

        if (user_repo.is_user_host(lobby_name, user_name)):
            await manager.broadcast_to_lobby_users(lobby_name, f"lobby_close")
            await manager.remove_all_user_from_lobby(lobby_name)
            await manager.broadcast_to_users_with_no_lobby(f"lobby_close, {lobby_name}")
        else:
            total_users = lobby_repo.get_amount_users(lobby_name)
            await manager.remove_user_from_lobby(lobby_name, user_name)
            await manager.broadcast_to_lobby_users(lobby_name, f"user_disconnect, {user_name}")
            await manager.broadcast_to_users_with_no_lobby(f"update_players, {lobby_name}, {total_users}")
            
        return  {'message': 'User left lobby successfully'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while leaving the lobby')

@app.post('/start_game/')
async def start_game(request: LobbyBase):
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
        await manager.broadcast_to_lobby_users(lobby_name, f"game_start")
        await manager.broadcast_to_users_with_no_lobby(f"game_start, {lobby_name}")
        game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while starting the game')
 
@app.get('/users_position/{lobby_name}')
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

@app.get('/user_hand/{lobby_name}/{user_name}') 
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
    game_repo = GameRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    # En esta sprint no estan las cartas de determinacion, fallaste y panico
    if (user_repo.get_total_cards(user_name) >= 5):
        raise HTTPException(status_code=406, detail='This user already has 5 cards')
    
    try:
        if (game_repo.get_game_status(lobby_name) == 'steal_card_stage_user_turn'):
            card_dict = game_logic.steal_card_from_deck(user_name) 
        else:   
            card_dict = game_logic.steal_card_from_deck_no_panic(user_name)
        
        if not (user_repo.is_user_in_quarantine(user_name)):
            await manager.broadcast_to_lobby_users(lobby_name, f"steal_card, {user_name}")
        else:
            await manager.broadcast_to_lobby_users(lobby_name, f"steal_card_with_quarantine, {user_name}, {card_dict['name']}")

        game_flow(lobby_name)
        return card_dict
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')

#! nuevo endpoint con cartas y jugadores posibles
@app.get('/play_combinations/{lobby_name}/{user_name}') 
async def get_play_combinations(lobby_name: str, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()  
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    try:
        return game_logic.get_play_combinations(lobby_name, user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the hand')

#! nuevo endpoint
@app.post('/choose_discard_or_play/')
async def choose_discard_or_play(request: ChooseDiscardOrPlayBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    discard_or_play = request.discard_or_play
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_repo = GameRepository()

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    try:
        game_repo.set_discard_or_play(lobby_name, discard_or_play)
        game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while choosing discard or play')

@app.post('/play_action_or_obstacule_card/')
async def play_card(request: PlayCardBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    target_user_name = request.target_user_name
    card_id = request.card_id
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_repo = GameRepository()
    card_repo = CardRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (user_repo.is_target_in_lobby(lobby_name, target_user_name)): #! El target puede ser el mismo usuario o alguien mas
        raise HTTPException(status_code=401, detail='This target user is not in the lobby')
    
    if not (user_repo.check_user_has_card(user_name, card_id)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    if not (user_repo.is_user_turn(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='It is not your turn')

    try:
        card_name = card_repo.get_card_name(card_id)
        game_repo.set_effect_to_be_applied(lobby_name, card_name)
        game_flow(lobby_name)
    except Exception as e:
        print(e)

@app.post('/discard_card/')
async def discard_card(lobby_name: str, user_name: str, id_card: int):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    card_repo = CardRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')

    if not (user_repo.check_user_has_card(user_name, id_card)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    if not (user_repo.is_user_turn(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='It is not your turn')
    
    if not (game_logic.can_card_be_discarded(id_card)):
        raise HTTPException(status_code=406, detail='This card cannot be discarded')
    
    try:
        game_logic.discard_card(user_name, id_card)

        if not (user_repo.is_user_in_quarantine(user_name)): 
            await manager.broadcast_to_lobby_users(lobby_name, f"card_dicard, {user_name}")
        else:
            card_dict = card_repo.get_card_dict(id_card)
            await manager.broadcast_to_lobby_users(lobby_name, f"card_dicard_with_quarantine, {user_name}, {card_dict['name']}")

        game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while playing the card')
    
@app.post('/swap_card/') #! Suponemos que el front eligio correctamente al usuario
async def swap_card(request: PlayCardBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    target_user_name = request.target_user_name
    card_id = request.card_id
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    card_repo = CardRepository()
    game_repo = GameRepository()
    game_logic = GameLogic()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (user_repo.is_target_in_lobby(lobby_name, target_user_name)): 
        raise HTTPException(status_code=401, detail='This target user is not in the lobby')
    
    if not (user_repo.check_user_has_card(user_name, card_id)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    if not (game_logic.validate_swap_card(user_name, card_id, target_user_name)):
        raise HTTPException(status_code=406, detail='You cannot swap this card')
    
    try:
        if (not game_repo.is_there_exchange_offer(lobby_name)): # No hay intercambio iniciado
            game_repo.set_exchange_card_start(lobby_name, card_id)
            game_repo.set_exchange_user_start(lobby_name, user_name)
            game_repo.set_exchange_user_finish(lobby_name, target_user_name)
            game_flow(lobby_name)
        else: # Hay intercambio iniciado
            game_repo.set_exchange_card_finish(lobby_name, card_id)
            user_start = game_repo.get_exchange_user_start(lobby_name)
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            card_start = game_repo.get_exchange_card_user_start(lobby_name)
            card_finish = game_repo.get_exchange_card_user_finish(lobby_name)
            game_logic.swap_card(lobby_name)

            if not (user_repo.is_user_in_quarantine(user_start)): # No esta en cuarentena
                await manager.broadcast_to_lobby_users(lobby_name, f"card_swap, {user_start}, {user_finish}")
            else: # Esta en cuarentena
                card_dict = card_repo.get_card_dict(card_start)
                await manager.broadcast_to_lobby_users(lobby_name, f"card_swap_with_quarantine, {user_start}, {user_finish}, {card_dict['name']}")

            if not (user_repo.is_user_in_quarantine(user_finish)): # No esta en cuarentena
                await manager.broadcast_to_lobby_users(lobby_name, f"card_swap, {user_finish}, {user_start}")
            else: # Esta en cuarentena
                card_dict = card_repo.get_card_dict(card_finish)
                await manager.broadcast_to_lobby_users(lobby_name, f"card_swap_with_quarantine, {user_finish}, {user_start}, {card_dict['name']}")
            
            game_flow(lobby_name)

    except Exception as e:
        raise HTTPException(status_code=500, detail='An error occurred while swapping the card')