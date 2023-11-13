from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.websockets = {}
        self.users_with_no_lobby = set()
        self.users_in_lobby = {}

    async def connect(self, websocket: WebSocket, user_name: str):
        await websocket.accept()

        if user_name in self.websockets:
            raise Exception("User WebSocket already exists")
        
        if len(self.users_with_no_lobby) == 0:
            self.users_with_no_lobby = set()

        self.websockets[user_name] = websocket
        self.users_with_no_lobby.add(user_name)

    async def disconnect(self, user_name: str):
        if user_name not in self.websockets:
            raise Exception("User WebSocket does not exist")
        
        self.websockets.pop(user_name)
        if user_name in self.users_with_no_lobby:
            self.users_with_no_lobby.remove(user_name)
        else:
            for lobby_name in self.users_in_lobby.keys():
                if user_name in self.users_in_lobby[lobby_name]:
                    self.users_in_lobby[lobby_name].remove(user_name)
                    
                    if len(self.users_in_lobby[lobby_name]) == 0:
                        self.users_in_lobby.pop(lobby_name)
                    break

    async def send_message(self, user_name: str, message: str):
        if user_name not in self.websockets:
            raise Exception("User WebSocket does not exist")
        
        connection = self.websockets[user_name]
        await connection.send_text(message)

    async def receive_message(self, user_name: str) -> str:
        if user_name not in self.websockets:
            raise Exception("User WebSocket does not exist")
        
        connection = self.websockets[user_name]
        return await connection.receive_text()

    async def broadcast_to_users_with_no_lobby(self, message: str):
        for user_name in self.users_with_no_lobby:
            await self.send_message(user_name, message)

    async def add_user_to_lobby(self, lobby_name: str, user_name: str):
        if user_name not in self.users_with_no_lobby:
            raise Exception("User does not exist")
        
        if lobby_name not in self.users_in_lobby.keys():
            self.users_in_lobby[lobby_name] = set()
        
        self.users_with_no_lobby.remove(user_name)
        self.users_in_lobby[lobby_name].add(user_name)

    async def remove_user_from_lobby(self, lobby_name: str, user_name: str):
        if lobby_name not in self.users_in_lobby.keys():
            raise Exception("Lobby does not exist")
        
        if user_name not in self.users_in_lobby[lobby_name]:
            raise Exception("User does not exist in Lobby")
        
        self.users_in_lobby[lobby_name].remove(user_name)
        self.users_with_no_lobby.add(user_name)

        if len(self.users_in_lobby[lobby_name]) == 0:
            self.users_in_lobby.pop(lobby_name)

    async def broadcast_to_lobby_users(self, lobby_name: str, message: str):
        if lobby_name not in self.users_in_lobby.keys():
            raise Exception("Lobby does not exist")
        
        for user_name in self.users_in_lobby[lobby_name]:
            await self.send_message(user_name, message)
        

    async def remove_all_user_from_lobby(self, lobby_name: str):
        if lobby_name not in self.users_in_lobby.keys():
            raise Exception("Lobby does not exist")
        
        users_in_lobby = self.users_in_lobby[lobby_name].copy()

        for user_name in users_in_lobby:
            await self.remove_user_from_lobby(lobby_name, user_name)