from pydantic import BaseModel

class UserBase(BaseModel):
    user_name: str

class CreateLobbyBase(BaseModel):
    lobby_name: str
    min_players: int
    max_players: int
    password: str
    host_name: str

class JoinLobbyBase(BaseModel):
    lobby_name: str
    password: str
    user_name: str

class LobbyBase(BaseModel):
    lobby_name: str
    user_name: str

class PlayCardBase(BaseModel):
    lobby_name: str
    user_name: str
    target_user_name: str
    card_id: int

class CardBase(BaseModel):
    lobby_name: str
    user_name: str
    card_id: int

class ChoiceBase(BaseModel):
    lobby_name: str
    user_name: str
    choice: str