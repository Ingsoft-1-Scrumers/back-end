from fastapi import FastAPI, HTTPException
from card_repository import CardRepository

app = FastAPI()

@app.get('/')
async def get_user_hand(user_name: str):
    card_repo = CardRepository()    #en realidad debería ser en UserRepository

    ''' no tengo esta fun en mi branch
    if not (user_repo.user_exists(user_name)):
        raise HTTPException(status_code=404, detail='This user does not exist')
    '''
    
    ''' hacerlo pero preguntando si el user está en la partida
    if not (lobby_repo.is_user_in_lobby(lobby_name, user_name)):
        raise HTTPException(status_code=401, detail='This user is not in the lobby')
    '''
    try:
        return card_repo.get_user_hand(user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while getting the hand')
    
@app.get('/')
async def steal_card_from_deck(user_name: str):
    card_repo = CardRepository()
    try:
        return card_repo.steal_card_from_deck(user_name)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail='An error occurred while stealing a card')
    