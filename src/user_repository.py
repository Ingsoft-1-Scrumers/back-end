from models import User
from pony.orm import db_session

class UserRepository:

    @db_session
    def create_user(self, user_name: str):
        User(name=user_name)

    @db_session
    def user_exists(self, user_name: str) -> bool:
        return User.exists(name=user_name)
    
    @db_session
    def is_user_in_a_lobby(self, user_name: str) -> bool:
        user = User.get(name=user_name)
        return user.lobby is not None
        
    @db_session
    def get_user(self, user_name: str) -> dict:
        user = User.get(name=user_name)
        if user is None:
            raise ValueError("User does not exist with name: {}".format(user_name))
        return {'id': user.id, 'Name': user.name}
