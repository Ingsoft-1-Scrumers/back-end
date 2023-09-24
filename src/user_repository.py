from models import User, db
from pony.orm import db_session

class UserRepository:

    @db_session
    def create_user(self, name):
        User(name=name)

    @db_session
    def check_unique_name(self, user_name: str) -> bool:
        return not User.exists(name=user_name)
        

    @db_session
    def get_user(self, user_id: int) -> dict:
        user = User.get(id=user_id)
        if user is None:
            raise ValueError("User does not exist with id: {}".format(user_id))
        return {'id': user.id, 'Name': user.name}
    
