from fastapi import FastAPI, HTTPException
from user_repository import UserRepository
from game_repository import GameRepository
from lobby_repository import LobbyRepository

app = FastAPI()

@app.post('/create_user/')
async def create_user(user_name: str):
    repo = UserRepository()
    if repo.check_unique_name(user_name):
        try:
            repo.create_user(name=user_name)
            return {'message': 'User created'}
        except Exception as e:
            return {'message': 'An error occurred while creating the user for exception: {}'.format(e)}
    else:
        raise HTTPException(status_code=400, detail='This username already exists')


@app.post('/start_game/')
async def start_game(game_name: str):
    repo_lobby = LobbyRepository()
    amount_players = repo_lobby.amount_players(game_name) #TODO Necesito esta funcion en lobby_repository 
    repo_game = GameRepository()
    try:
        repo_game.create_Game(game_name, amount_players)
        return {'message': 'Game started successfully'}
    except Exception as e:
        return {'message': 'An error occurred while starting the game for cause: {}'.format(e)}



"""
@app.get('/user/{user_id}')
async def get_user(user_id: int):
    repo = UserRepository()
    try:
        return repo.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
"""