from models import Position, User, Game
from pony.orm import db_session

class PositionRepository:

    @db_session
    def create_position(self, user: User, game: Game, turn):
        Position(user=user, game=game, turn=turn)

    