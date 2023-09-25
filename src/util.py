from models import User, Position
#import random
from typing import List

# Toma una lista de usuarios que provee el lobby
def assign_positions(users: List[User]) -> List[Position]:
    result = []
    for user in users:
        result.append(Position(user=user))
    return result