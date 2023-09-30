from models import Game, User, db
from pony.orm import db_session, Set
from user_repository import UserRepository
#from card_repository import CardRepository

class GameRepository:

    #crear game necesita el nombre del juego y la cantidad de jugadores
    @db_session
    def create_Game(self, name: str, amount_players: int):
        Game(name=name, amount_players=amount_players)

       
    #obtener todas las cartas de un juego
    @db_session
    def get_all_cards_this_game(self, name: str):
        repo_card_Repository = CardRepository()
        Game.lobby.get(name=name).all_cards = repo_card_Repository.create_cards_for_this_game(name)

    #obtener el conjunto de usuarios de un juego
    @db_session
    def give_users(self, name: str) -> Set(User):
        repo_user = UserRepository()
        return repo_user.get_all_users()
