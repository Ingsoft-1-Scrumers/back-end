from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from connection import ConnectionManager
from repository import *
from util import *
from basemodels import *
from settings import *

app = FastAPI()
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def exchange_stage(lobby_name : str, user_start : str, user_finish : str, out_of_order : bool = False):
    user_repo = UserRepository()
    game_repo = GameRepository()
    game_logic = GameLogic()
    superinfection = game_logic.exchange_with_superinfection(user_start, user_finish)
    obstacle = game_logic.is_there_obstacle(lobby_name, user_start)

    if (obstacle and not out_of_order): # Hay obstaculo
        await end_turn(lobby_name)
    elif (user_repo.is_user_in_quarantine(user_finish)): # Si el objetivo esta en cuarentena
        await end_turn(lobby_name)
    elif (superinfection): # Hay superinfeccion
        if (game_logic.superinfection(user_start)):
            game_logic.play_card(lobby_name, user_finish, user_start, "Lanzallamas")
            await manager.broadcast_to_lobby_users(lobby_name, f"superinfection, {user_start}")
        else:
            game_logic.play_card(lobby_name, user_start, user_finish, "Lanzallamas")
            await manager.broadcast_to_lobby_users(lobby_name, f"superinfection, {user_finish}")

        victory = game_logic.victory(lobby_name) 

        if (victory):
            team_winners = game_logic.team_winners(lobby_name)
            list_winners = game_logic.list_winners(lobby_name)
            await manager.broadcast_to_lobby_users(lobby_name, f"game_over")
            await manager.broadcast_to_lobby_users(lobby_name, f"winners, {team_winners}, {' - '.join(list_winners)}")
            await manager.remove_all_user_from_lobby(lobby_name)
            game_logic.end_game(lobby_name)
        else:
            await end_turn(lobby_name)

    else: # Hay intercambio de cartas
        game_repo.set_game_status(lobby_name, "start_exchange")
        await manager.send_message(user_start, f"start_exchange, {user_finish}")

async def applied_effect(lobby_name : str, target_user_name : str, effect_to_be_applied : str):
    game_repo = GameRepository()
    game_logic = GameLogic()
    user_repo = UserRepository()
    card_repo = CardRepository()
    user_turn = game_repo.get_turn_user(lobby_name)
    user_finish = game_logic.next_player(lobby_name, user_turn)
    lose_condition = False
    out_of_order = False

    match effect_to_be_applied:
        case 'Seduccion':
            user_finish = target_user_name
            out_of_order = True
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
        
        case 'Sospecha':
            random_card = user_repo.get_random_card_from_hand(target_user_name)
            card_name = card_repo.get_card_name(random_card)
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
            await manager.send_message(user_turn, f"sospecha, {target_user_name}, {card_name}")

        case 'Whisky':
            user_cards = user_repo.get_user_cards(user_turn)
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
            await manager.broadcast_to_lobby_users(lobby_name, f"whisky, {user_turn}, {user_cards}")
            lose_condition = game_logic.flamethrower_lose_condition(user_turn)
            user_cosa = user_turn 

        case 'Analisis':
            user_cards = user_repo.get_user_cards(target_user_name)
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
            await manager.send_message(user_turn, f"analisis, {target_user_name}, {user_cards}")
            lose_condition = game_logic.flamethrower_lose_condition(target_user_name) and (user_repo.get_role(user_turn) == "Humano")
            user_cosa = target_user_name
        
        case 'Mas vale que corras' | 'Cambio de lugar':
            game_logic.play_card(lobby_name, user_turn, target_user_name, effect_to_be_applied)
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
            user_finish = game_logic.next_player(lobby_name, user_turn)

        case _: # Resto de Cartas
            game_logic.play_card(lobby_name, user_turn, target_user_name, effect_to_be_applied)
            await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
            user_finish = game_logic.next_player(lobby_name, user_turn)
    
    game_repo.set_effect_to_be_applied(lobby_name, "None")
    game_repo.set_target_to_be_afflicted(lobby_name, "None")

    if (lose_condition):
        game_logic.play_card(lobby_name, user_cosa, user_cosa, "Lanzallamas")
        await manager.broadcast_to_lobby_users(lobby_name, f"cosa_con_lanzallamas, {user_cosa}")

    victory = game_logic.victory(lobby_name)
    
    if (victory):
        team_winners = game_logic.team_winners(lobby_name)
        list_winners = game_logic.list_winners(lobby_name)
        await manager.broadcast_to_lobby_users(lobby_name, f"game_over")
        await manager.broadcast_to_lobby_users(lobby_name, f"winners, {team_winners}, {' - '.join(list_winners)}")
        await manager.remove_all_user_from_lobby(lobby_name)
        game_logic.end_game(lobby_name)
    else:
        await exchange_stage(lobby_name, user_turn, user_finish, out_of_order)

async def end_turn(lobby_name : str):
    game_repo = GameRepository()
    game_logic = GameLogic()
    user_repo = UserRepository()
    user_turn = game_repo.get_turn_user(lobby_name)

    if (user_repo.is_user_in_quarantine(user_turn)):
        user_repo.decrease_quarantine(user_turn)

    direction = game_repo.get_direction(lobby_name)
    game_logic.next_turn(lobby_name, direction)
    user_next_turn = game_repo.get_turn_user(lobby_name)
    game_repo.set_game_status(lobby_name, "steal_card_stage")
        
    await manager.send_message(user_turn, f"turn_ended")
    await manager.broadcast_to_lobby_users(lobby_name, f"turn, {user_next_turn}")
    await manager.send_message(user_next_turn, f"steal_card_stage")

async def game_flow(lobby_name : str):
    user_repo = UserRepository() 
    lobby_repo = LobbyRepository()
    game_repo = GameRepository()
    card_repo = CardRepository()
    game_logic = GameLogic()
    game_status = game_repo.get_game_status(lobby_name)
    user_turn = game_repo.get_turn_user(lobby_name)

    match game_status:
        case 'game_not_started':
            if (lobby_repo.is_everyone_ready(lobby_name)):
                lobby_repo.set_everyone_ready_false(lobby_name)
                game_repo.set_game_status(lobby_name, "steal_card_stage")
                await manager.broadcast_to_lobby_users(lobby_name, f"turn, {user_turn}")
                await manager.send_message(user_turn, f"steal_card_stage")

        case 'steal_card_stage':
            if (game_repo.get_effect_to_be_applied(lobby_name) == "Panico"):
                game_repo.set_effect_to_be_applied(lobby_name, "None")
                game_repo.set_game_status(lobby_name, f"play_panic")
                await manager.send_message(user_turn, f"play_panic")
            else:
                game_repo.set_game_status(lobby_name, "discard_or_play")
                await manager.send_message(user_turn, f"discard_or_play")

        case 'play_panic':
            target_user_name = game_repo.get_target_to_be_afflicted(lobby_name)
            effect_to_be_applied = game_repo.get_effect_to_be_applied(lobby_name)
            game_repo.set_effect_to_be_applied(lobby_name, "None")
            game_repo.set_target_to_be_afflicted(lobby_name, "None")

            match effect_to_be_applied:
                case "Cita a ciegas":
                    game_repo.set_game_status(lobby_name, "steal_after_panic")
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await manager.send_message(user_turn, f"steal_after_panic")

                case '¡Ups!':
                    user_cards = user_repo.get_user_cards(user_turn)
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await manager.broadcast_to_lobby_users(lobby_name, f"¡ups!, {user_turn}, {user_cards}")
                    lose_condition = game_logic.flamethrower_lose_condition(user_turn)
                    
                    if (lose_condition):
                        game_logic.play_card(lobby_name, user_turn, user_turn, "Lanzallamas")
                        team_winners = game_logic.team_winners(lobby_name)
                        list_winners = game_logic.list_winners(lobby_name)
                        await manager.broadcast_to_lobby_users(lobby_name, f"cosa_con_lanzallamas, {user_turn}")
                        await manager.broadcast_to_lobby_users(lobby_name, f"game_over")
                        await manager.broadcast_to_lobby_users(lobby_name, f"winners, {team_winners}, {' - '.join(list_winners)}")
                        await manager.remove_all_user_from_lobby(lobby_name)
                        game_logic.end_game(lobby_name)
                    else:
                        await exchange_stage(lobby_name, user_turn, user_finish)

                case 'Que quede entre nosotros':
                    user_cards = user_repo.get_user_cards(user_turn)
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
                    await manager.send_message(target_user_name, f"que quede entre nosotros, {user_turn}, {user_cards}")
                    lose_condition = game_logic.flamethrower_lose_condition(user_turn) and (user_repo.get_role(target_user_name) == "Humano")

                    if (lose_condition):
                        game_logic.play_card(lobby_name, user_turn, user_turn, "Lanzallamas")
                        team_winners = game_logic.team_winners(lobby_name)
                        list_winners = game_logic.list_winners(lobby_name)
                        await manager.broadcast_to_lobby_users(lobby_name, f"cosa_con_lanzallamas, {user_turn}")
                        await manager.broadcast_to_lobby_users(lobby_name, f"game_over")
                        await manager.broadcast_to_lobby_users(lobby_name, f"winners, {team_winners}, {' - '.join(list_winners)}")
                        await manager.remove_all_user_from_lobby(lobby_name)
                        game_logic.end_game(lobby_name)
                    else:
                        await exchange_stage(lobby_name, user_turn, user_finish)
                    
                case 'Cuerdas podridas':
                    game_logic.delete_all_quarantine(lobby_name)
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)
                
                case 'No podemos ser amigos':
                    if (target_user_name == user_turn):
                        user_finish = game_logic.next_player(lobby_name, user_turn)
                    else:
                        user_finish = target_user_name
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, target_user_name, True)

                case 'Sal de aqui':
                    if (target_user_name == user_turn):
                        user_finish = game_logic.next_player(lobby_name, user_turn)
                    else:
                        game_logic.play_card(lobby_name, user_turn, target_user_name, "Mas vale que corras")
                        user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)

                case 'Uno, dos':
                    if (target_user_name == user_turn):
                        user_finish = game_logic.next_player(lobby_name, user_turn)
                    else:
                        game_logic.play_card(lobby_name, user_turn, target_user_name, "Mas vale que corras")
                        user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {target_user_name}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)
                    
                case 'Tres, cuatro':
                    game_logic.delete_all_doors(lobby_name)
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)

                case 'Es aqui la fiesta':
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    game_logic.delete_all_doors(lobby_name)
                    game_logic.delete_all_quarantine(lobby_name)
                    game_logic.swap_position_party(lobby_name)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)

                case _: #! Acan caen Olvidadizo, Revelaciones y Vuelta y Vuelta
                    user_finish = game_logic.next_player(lobby_name, user_turn)
                    await manager.broadcast_to_lobby_users(lobby_name, f"play_card, {user_turn}, {user_turn}, {effect_to_be_applied}")
                    await exchange_stage(lobby_name, user_turn, user_finish)

        case 'steal_after_panic':
            game_repo.set_game_status(lobby_name, "discard_after_panic")
            await manager.send_message(user_turn, f"discard_after_panic")

        case 'discard_after_panic':
            await end_turn(lobby_name)
        
        case 'discard_or_play':
            choice = game_repo.get_discard_or_play(lobby_name)
            game_repo.set_discard_or_play(lobby_name, "None")

            if (choice == 'discard'): # Descartar
                user_next_turn = game_logic.next_player(lobby_name, user_turn)
                await exchange_stage(lobby_name, user_turn, user_next_turn)
            else: # Jugar
                target_user_name = game_repo.get_target_to_be_afflicted(lobby_name)
                effect_to_be_applied = game_repo.get_effect_to_be_applied(lobby_name)
                defense = game_logic.can_user_defend_play(target_user_name, effect_to_be_applied)

                if (defense): # El target puede defenderse 
                    game_repo.set_game_status(lobby_name, "defend_or_skip")
                    await manager.send_message(user_turn, f"waiting_target_defense")
                    await manager.send_message(target_user_name, f"defend_or_skip, {user_turn}, {effect_to_be_applied}")
                else: # El target no puede defenderse
                    await applied_effect(lobby_name, target_user_name, effect_to_be_applied)
   
        case 'defend_or_skip':
            choice = game_repo.get_defend_or_skip(lobby_name)
            target_user_name = game_repo.get_target_to_be_afflicted(lobby_name)
            effect_to_be_applied = game_repo.get_effect_to_be_applied(lobby_name)

            if (choice == "skip"): # No quiere defenderse
                game_repo.set_defend_or_skip(lobby_name, "None")
                await applied_effect(lobby_name, target_user_name, effect_to_be_applied)
            else: # Quiere defenderse
                game_repo.set_defend_or_skip(lobby_name, "None")
                game_repo.set_game_status(lobby_name, "defend_play")
                await manager.send_message(target_user_name, f"defend_play, {user_turn}, {effect_to_be_applied}")

        case 'defend_play':
            target_user_name = game_repo.get_target_to_be_afflicted(lobby_name)
            effect_to_be_applied = game_repo.get_effect_to_be_applied(lobby_name)
            game_repo.set_effect_to_be_applied(lobby_name, "None")
            game_repo.set_target_to_be_afflicted(lobby_name, "None")
            game_repo.set_game_status(lobby_name, "steal_after_defend")

            await manager.broadcast_to_lobby_users(lobby_name, f"defense_play, {target_user_name}, {user_turn}, {effect_to_be_applied}")
            await manager.send_message(target_user_name, f"steal_after_defend")

        case 'steal_after_defend':
            user_next_turn = game_logic.next_player(lobby_name, user_turn)
            await exchange_stage(lobby_name, user_turn, user_next_turn)
            
        case 'start_exchange':
            user_start = game_repo.get_exchange_user_start(lobby_name)
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            defense = game_logic.can_user_defend_exchange(user_finish)
            await manager.send_message(user_start, f"waiting_for_exchange")

            if (defense): # Se puede defender
                game_repo.set_game_status(lobby_name, "defend_or_exchange")
                await manager.send_message(user_finish, f"defend_or_exchange, {user_start}")
            else: # No se puede defender
                game_repo.set_game_status(lobby_name, "finish_exchange")
                await manager.send_message(user_finish, f"finish_exchange, {user_start}")

        case 'defend_or_exchange':
            user_start = game_repo.get_exchange_user_start(lobby_name)
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            choice = game_repo.get_defend_or_exchange(lobby_name)
            game_repo.set_defend_or_exchange(lobby_name, "None")
        
            if (choice == 'defense'): # Quiere defenderse
                game_repo.set_game_status(lobby_name, "defend_exchange")
                await manager.send_message(user_finish, f"defend_exchange, {user_start}")
            else: # No quiere defenderse
                game_repo.set_game_status(lobby_name, "finish_exchange")
                await manager.send_message(user_finish, f"finish_exchange, {user_start}")

        case 'defend_exchange':
            effect_to_be_applied = game_repo.get_effect_to_be_applied(lobby_name)
            user_start = game_repo.get_exchange_user_start(lobby_name)
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            card_start = game_repo.get_exchange_card_user_start(lobby_name)

            game_repo.set_effect_to_be_applied(lobby_name, "None")
            game_repo.clean_exchange_data(lobby_name)
            game_repo.set_game_status(lobby_name, "steal_after_exchange")

            match effect_to_be_applied:
                case 'Aterrador':
                    card_start_name = card_repo.get_card_name(card_start)
                    await manager.send_message(user_finish, f"aterrador, {user_start}, {card_start_name}")
                case 'Fallaste': 
                    user_finish_next_user = game_logic.next_player(lobby_name, user_finish)
                    game_repo.set_exchange_user_finish(lobby_name, user_finish_next_user)
                    game_repo.set_game_status(lobby_name, "steal_after_fallaste")
                    
            await manager.broadcast_to_lobby_users(lobby_name, f"defense_play, {user_finish}, {user_start}, swap")
            await manager.send_message(user_finish, f"steal_after_exchange")

        case 'steal_after_fallaste':
            user_finish_next_user = game_repo.get_exchange_user_finish(lobby_name)
            user_finish = game_logic.previous_player(lobby_name, user_finish_next_user)
            obstacle = game_logic.is_there_obstacle(lobby_name, user_finish)
            game_repo.clean_exchange_data(lobby_name)

            if (user_finish_next_user == user_turn):
                await end_turn(lobby_name)
            elif (obstacle):
                await end_turn(lobby_name)
            else:
                await exchange_stage(lobby_name, user_turn, user_finish_next_user, True)

        case 'steal_after_exchange':
            await end_turn(lobby_name)

        case 'finish_exchange':
            game_repo.clean_exchange_data(lobby_name)
            game_repo.set_effect_to_be_applied(lobby_name, "None")
            victory = game_logic.victory(lobby_name)

            if (victory):
                team_winners = game_logic.team_winners(lobby_name)
                list_winners = game_logic.list_winners(lobby_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"game_over")
                await manager.broadcast_to_lobby_users(lobby_name, f"winners, {team_winners}, {' - '.join(list_winners)}")
                await manager.remove_all_user_from_lobby(lobby_name)
                game_logic.end_game(lobby_name)
            else:
                await end_turn(lobby_name)

@app.websocket('/websocket/{user_name}')
async def lobby_listing(websocket: WebSocket, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()

    await manager.connect(websocket, user_name)
    try:
        while True:
            pass
            message = await manager.receive_message(user_name)
            is_in_lobby = user_repo.is_user_in_a_lobby(user_name)

            if (is_in_lobby):
                lobby_name = user_repo.get_user_lobby(user_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"chat_msg, {user_name}, {message}")
            else:
                raise HTTPException(status_code=401, detail='This user is not in a lobby')
            
    except WebSocketDisconnect:
        is_in_lobby = user_repo.is_user_in_a_lobby(user_name)

        if (not is_in_lobby):
            await manager.disconnect(user_name)
        else:
            lobby_name = user_repo.get_user_lobby(user_name)

            if (lobby_repo.is_game_started(lobby_name)):
                await manager.disconnect(user_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"user_disconnect_in_game, {user_name}")
                await manager.remove_all_user_from_lobby(lobby_name)
                game_logic.end_game(lobby_name)                
            else:
                if (user_repo.is_user_host(lobby_name, user_name) and lobby_repo.get_amount_users(lobby_name) == 1):
                    lobby_repo.leave_lobby(lobby_name, user_name)
                    await manager.disconnect(user_name)
                    await manager.broadcast_to_users_with_no_lobby(f"lobby_close, {lobby_name}")
                elif (user_repo.is_user_host(lobby_name, user_name)):
                    lobby_repo.leave_lobby(lobby_name, user_name)
                    await manager.disconnect(user_name)
                    await manager.broadcast_to_lobby_users(lobby_name, f"lobby_close")
                    await manager.remove_all_user_from_lobby(lobby_name)
                    await manager.broadcast_to_users_with_no_lobby(f"lobby_close, {lobby_name}")
                else:
                    lobby_repo.leave_lobby(lobby_name, user_name)
                    await manager.disconnect(user_name)
                    await manager.broadcast_to_lobby_users(lobby_name, f"user_disconnect, {user_name}")
                    total_users = lobby_repo.get_amount_users(lobby_name)
                    await manager.broadcast_to_users_with_no_lobby(f"update_players, {lobby_name}, {total_users}")
                    
        user_repo.remove_user(user_name)

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

        if ENVIRONMENT != 'test':
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
async def get_joinable_lobbies():
    lobby_repo = LobbyRepository()
    
    try:
        return lobby_repo.get_joinable_lobby_listings()
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
        if ENVIRONMENT != 'test':
            await manager.broadcast_to_lobby_users(lobby_name, f"user_connect, {user_name}")
            await manager.add_user_to_lobby(lobby_name, user_name)
            await manager.broadcast_to_users_with_no_lobby(f"update_players, {lobby_name}, {total_users}")
        return {'message': 'Joined lobby'}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while joining the lobby')

@app.get('/lobby_users/{lobby_name}')
async def get_lobby_users(lobby_name: str):
    lobby_repo = LobbyRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
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
        if ENVIRONMENT != 'test':
            if (user_repo.is_user_host(lobby_name, user_name) and lobby_repo.get_amount_users(lobby_name) == 1):
                lobby_repo.leave_lobby(lobby_name, user_name)
                await manager.remove_all_user_from_lobby(lobby_name)
                await manager.broadcast_to_users_with_no_lobby(f"lobby_close, {lobby_name}")
            elif (user_repo.is_user_host(lobby_name, user_name)):
                lobby_repo.leave_lobby(lobby_name, user_name)
                await manager.remove_user_from_lobby(lobby_name, user_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"lobby_close")
                await manager.remove_all_user_from_lobby(lobby_name)
                await manager.broadcast_to_users_with_no_lobby(f"lobby_close, {lobby_name}")
            else:
                lobby_repo.leave_lobby(lobby_name, user_name)
                await manager.remove_user_from_lobby(lobby_name, user_name)
                await manager.broadcast_to_lobby_users(lobby_name, f"user_disconnect, {user_name}")
                total_users = lobby_repo.get_amount_users(lobby_name)
                await manager.broadcast_to_users_with_no_lobby(f"update_players, {lobby_name}, {total_users}")
        else:
            lobby_repo.leave_lobby(lobby_name, user_name)

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
        if ENVIRONMENT != 'test':
            game_logic.start_game(lobby_name)
            await manager.broadcast_to_lobby_users(lobby_name, f"game_start")
            await manager.broadcast_to_users_with_no_lobby(f"game_start, {lobby_name}")
            await game_flow(lobby_name)
        else:
            game_logic.start_game(lobby_name)
            return {'message': 'Game started'}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while starting the game')

@app.post('/ready/')
async def ready(request: LobbyBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()

    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if (not lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started')

    try:
        user_repo.set_user_ready(user_name, True)
        if ENVIRONMENT != 'test':
            await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while setting the user as ready')

@app.get('/users_position/{lobby_name}')
async def get_users_position(lobby_name: str):
    lobby_repo = LobbyRepository()
    game_repo = GameRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
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

@app.get('/user_cards_info/{lobby_name}/{user_name}') 
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
        return game_logic.get_play_combinations(user_name, lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the hand')

@app.get('/get_user_role/{lobby_name}/{user_name}')
async def get_user_role(lobby_name: str, user_name: str):
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    
    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started')
    
    try:
        role = user_repo.get_role(user_name)
        return {'role': role}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An internal error occurred')

@app.post('/steal_card/')
async def steal_card(request: LobbyBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
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
    
    try:
        if (game_repo.get_game_status(lobby_name) == 'steal_card_stage'):
            card_dict = game_logic.steal_card_from_deck(user_name)
            if (card_dict["type"] == "Panico"):
                game_repo.set_effect_to_be_applied(lobby_name, "Panico")
        else:   
            card_dict = game_logic.steal_card_from_deck_no_panic(user_name)
        
        if ENVIRONMENT != 'test':
            if (user_repo.is_user_in_quarantine(user_name)):
                await manager.broadcast_to_lobby_users(lobby_name, f"steal_card, {user_name}, {card_dict['name']}")
            else:
                await manager.broadcast_to_lobby_users(lobby_name, f"steal_card, {user_name}")

            await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')

@app.post('/discard_card/')
async def discard_card(request: CardBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    id_card = request.card_id
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    card_repo = CardRepository()
    game_logic = GameLogic()
    game_repo = GameRepository()
    
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
    
    if not (game_logic.can_card_be_discarded(user_name, id_card)):
        raise HTTPException(status_code=406, detail='This card cannot be discarded')
    
    try:
        game_logic.discard_card(user_name, id_card)

        if ENVIRONMENT != 'test':
            if (user_repo.is_user_in_quarantine(user_name)):
                card_dict = card_repo.get_card_dict(id_card)
                await manager.broadcast_to_lobby_users(lobby_name, f"discard_card, {user_name}, {card_dict['name']}")
            else:
                await manager.broadcast_to_lobby_users(lobby_name, f"discard_card, {user_name}")

            game_repo.set_discard_or_play(lobby_name, "discard")
            await game_flow(lobby_name)
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while discarding the card')

#! Suponemos que el Front elige la combinacion correcta
@app.post('/play_card/')
async def play_card(request: PlayCardBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    target_user_name = request.target_user_name
    card_id = request.card_id
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()
    game_repo = GameRepository()
    card_repo = CardRepository()
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (user_repo.check_user_has_card(user_name, card_id)):
        raise HTTPException(status_code=401, detail='This user does not have this card')
    
    if not (user_repo.is_user_turn(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='It is not your turn')

    try:
        if (game_repo.get_game_status(lobby_name) == "discard_or_play"):
            game_repo.set_discard_or_play(lobby_name, "play")
        
        game_logic.discard_card(user_name, card_id)
        card_name = card_repo.get_card_name(card_id)
        game_repo.set_effect_to_be_applied(lobby_name, card_name)
        game_repo.set_target_to_be_afflicted(lobby_name, target_user_name)
        await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while playing the card')

@app.post('/defend_or_skip/')
async def defend_or_skip(request: ChoiceBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    choice = request.choice
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
        if (choice == "defense"):
            game_repo.set_defend_or_skip(lobby_name, "defense")
        else:
            game_repo.set_defend_or_skip(lobby_name, "skip")
        await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while choosing defend or skip')

@app.post('/defend_or_exchange/')
async def defend_or_exchange(request: ChoiceBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    choice = request.choice
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
        if (choice == "defense"):
            game_repo.set_defend_or_exchange(lobby_name, "defense")
        else:
            game_repo.set_defend_or_exchange(lobby_name, "exchange")
        await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while choosing defend or exchange')

@app.post('/defense_card/')
async def defense_card(request: CardBase):
    lobby_name = request.lobby_name
    user_name = request.user_name
    card_id = request.card_id
    user_repo = UserRepository()
    lobby_repo = LobbyRepository()
    game_logic = GameLogic()
    game_repo = GameRepository()
    card_repo = CardRepository()

    card_name = card_repo.get_card_name(card_id)
    
    if not (lobby_repo.lobby_exists(lobby_name)):
        raise HTTPException(status_code=404, detail='This lobby name does not exist')
    
    if not (lobby_repo.is_game_started(lobby_name)):
        raise HTTPException(status_code=406, detail='This game has not started yet')

    if not (user_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    
    if not (user_repo.check_user_has_card(user_name, card_id)):
        raise HTTPException(status_code=401, detail='This user does not have this card')

    if not (game_logic.can_card_cancel_effect(lobby_name, card_name)):
        raise HTTPException(status_code=401, detail='This card cannot cancel the effect')

    try:
        game_repo.set_effect_to_be_applied(lobby_name, card_name)
        game_logic.discard_card(user_name, card_id)
        await game_flow(lobby_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while defending the card')
       
#! Suponemos que el front eligio correctamente al usuario   
@app.post('/swap_card/')
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
            game_repo.set_effect_to_be_applied(lobby_name, "swap_card")
        else: # Hay intercambio iniciado
            game_repo.set_exchange_card_finish(lobby_name, card_id)
            game_logic.swap_card(lobby_name)
            user_start = game_repo.get_exchange_user_start(lobby_name)
            user_finish = game_repo.get_exchange_user_finish(lobby_name)
            card_start = game_repo.get_exchange_card_user_start(lobby_name)
            
            if ENVIRONMENT != 'test':
                if (user_repo.is_user_in_quarantine(user_start)): # Usuario que inicio el intercambio esta en cuarentena
                    card_dict = card_repo.get_card_dict(card_start)
                    await manager.broadcast_to_lobby_users(lobby_name, f"card_swap, {user_start}, {user_finish}, {card_dict['name']}")
                else: 
                    await manager.broadcast_to_lobby_users(lobby_name, f"card_swap, {user_start}, {user_finish}")
                      
        await game_flow(lobby_name)  
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while swapping the card')
    