from pydantic import BaseModel
from fastapi import WebSocket

class CreateUserRequest(BaseModel):
    user_name: str

class CreateLobbyRequest(BaseModel):
    lobby_name: str
    min_players: int
    max_players: int
    password: str
    host_name: str

class JoinLobbyRequest(BaseModel):
    lobby_name: str
    password: str
    user_name: str

class StartGameRequest(BaseModel):
    lobby_name: str
    user_name: str

class LobbyUserRequest(BaseModel):
    user_name: str

class PlayCardRequest(BaseModel):
    lobby_name: str
    user_name: str
    target_user_name: str
    card_id: int

class EndLobbyUserRequest(BaseModel):
    lobby_name: str
    user_name: str