from models import Position
from pony.orm import db_session

class PositionRepository:

    @db_session
    def create_position(self, user, game, turn):
        Position(user=user, game=game, turn=turn)

    