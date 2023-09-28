from models import User, Position, Game
from typing import List, Set

# Toma una lista de usuarios que provee el lobby
def assign_positions(users: Set(User), game: Game) -> List[Position]:
    result = []
    for user in users:
        result.append(Position(user=user, game=game))
    return result