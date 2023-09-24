from fastapi import FastAPI, HTTPException
from user_repository import UserRepository

app = FastAPI()

@app.post('/create_user/')
async def create_user(user_name: str):
    repo = UserRepository()
    if repo.check_unique_name(user_name):
        try:
            repo.create_user(name=user_name)
            return {'message': 'User created'}
        except Exception as e:
            return {'message': 'An error occurred while creating the user'}
    else:
        raise HTTPException(status_code=400, detail='This username already exists')


"""
@app.get('/user/{user_id}')
async def get_user(user_id: int):
    repo = UserRepository()
    try:
        return repo.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
"""