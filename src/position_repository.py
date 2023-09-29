from models import Position, User, Game
from pony.orm import db_session

class PositionRepository:

    @db_session
    def create_position(self, user: User, game: Game, turn):
        Position(user=user, game=game, turn=turn)

    @db_session
    def get_position(user: User) -> dict:
        position = Position.get(user=user)
        if position is None:
            raise ValueError("Position does not exist")
        return {'username': user.name, 'position': position.id}