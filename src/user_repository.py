from models import User, db
from pony.orm import db_session, Set

class UserRepository:

    #crear usuario
    @db_session
    def create_user(self, name):
        User(name=name)

    #chequear si el nombre de usuario es unico
    @db_session
    def check_unique_name(self, user_name: str) -> bool:
        return not User.exists(name=user_name)

    #obtener un usuario por id
    @db_session
    def get_user(self, user_id: int) -> dict:
        user = User.get(id=user_id)
        if user is None:
            raise ValueError("User does not exist with id: {}".format(user_id))
        return {'id': user.id, 'Name': user.name}

    #obtener todos los usuarios de un game
    @db_session
    def get_all_users(self, game_name: str) -> Set(User):
        return User.select(lambda u: u.lobby.name == game_name)

    #matar a un usuario
    @db_session
    def knock_out_user(self, name: str):
        try:
            User.get(name=name).is_alive = False
        except:
            raise ValueError("User does not exist with name: {}".format(name))