from fastapi import WebSocket, HTTPException

class ConnectionManager:
    def __init__(self):
        self.user_connections: dict[str, WebSocket] = {}
        self.lobby_connections: dict[str, dict[str, WebSocket]] = {}
        self.game_connections: dict[str, dict[str, WebSocket]] = {}

    # User Connections
    async def user_connect(self, websocket: WebSocket, user_name: str):
        await websocket.accept()

        if user_name in self.user_connections:
            raise HTTPException(status_code= 400, detail= "User WebSocket already exists")
        
        self.user_connections[user_name] = websocket
        
    async def user_disconnet(self, user_name: str):
        if user_name not in self.user_connections:
            raise Exception("User WebSocket does not exist")
        
        self.user_connections.pop(user_name)

    async def close_user_connections(self):
        for user_name, connection in self.user_connections.items():
            await connection.close()
            self.user_connections.pop(user_name)

    async def send_message_to_user(self, user_name: str, message: str):
        if user_name not in self.user_connections:
            raise Exception("User WebSocket does not exist")
        
        connection = self.user_connections[user_name]
        await connection.send_text(message)

    async def user_connection_sleep(self, user_name: str):
        if user_name not in self.user_connections:
            raise Exception("User WebSocket does not exist")
        
        connection = self.user_connections[user_name]
        await connection.receive_text()

    async def broadcast_to_users(self, message: str):
        for connection in self.user_connections.values():
            await connection.send_text(message)
        
    # Lobby Connections
    async def lobby_user_connect(self, websocket: WebSocket, lobby_name: str, user_name: str):
        await websocket.accept()

        if lobby_name not in self.lobby_connections:
            self.lobby_connections[lobby_name] = {}

        if user_name in self.lobby_connections[lobby_name]:
            raise HTTPException(status_code= 400, detail= "Lobby User WebSocket already")
        
        self.lobby_connections[lobby_name][user_name] = websocket

    async def lobby_user_disconnect(self, lobby_name: str, user_name: str):
        if lobby_name not in self.lobby_connections:
            raise Exception("Lobby does not exist")

        if user_name not in self.lobby_connections[lobby_name]:
            raise Exception("Lobby User WebSocket does not exist")
        
        self.lobby_connections[lobby_name].pop(user_name)

        if len(self.lobby_connections[lobby_name]) == 0:
            self.lobby_connections.pop(lobby_name)

    async def close_lobby_connections(self, lobby_name: str):
        if lobby_name not in self.lobby_connections:
            raise Exception("Lobby does not exist")
        
        for user_name, connection in self.lobby_connections[lobby_name].items():
            await connection.close()
            self.lobby_connections[lobby_name].pop(user_name)
        self.lobby_connections.pop(lobby_name)
    
    async def send_message_to_lobby_user(self, lobby_name: str, user_name: str, message: str):
        if lobby_name not in self.lobby_connections:
            raise Exception("Lobby does not exist")

        if user_name not in self.lobby_connections[lobby_name]:
            raise Exception("Lobby User WebSocket does not exist")

        connection = self.lobby_connections[lobby_name][user_name]
        await connection.send_text(message)

    async def receive_message_from_lobby_user(self, lobby_name: str, user_name: str) -> str:
        if lobby_name not in self.lobby_connections:
            raise Exception("Lobby does not exist")

        if user_name not in self.lobby_connections[lobby_name]:
            raise Exception("Lobby User WebSocket does not exist")

        connection = self.lobby_connections[lobby_name][user_name]
        return await connection.receive_text()

    async def broadcast_to_lobby(self, lobby_name: str, message: str):
        if lobby_name not in self.lobby_connections:
            raise Exception("Lobby does not exist")

        for connection in self.lobby_connections[lobby_name].values():
            await connection.send_text(message)
    
    # Game User Connections
    async def game_user_connect(self, websocket: WebSocket, game_name: str, user_name: str):
        await websocket.accept()

        if game_name not in self.game_connections:
            self.game_connections[game_name] = {}

        if user_name in self.game_connections[game_name]:
            raise HTTPException(status_code= 400, detail= "Game User WebSocket already")
        
        self.game_connections[game_name][user_name] = websocket

    async def game_user_disconnect(self, game_name: str, user_name: str):
        if game_name not in self.game_connections:
            raise Exception("Game does not exist")

        if user_name not in self.game_connections[game_name]:
            raise Exception("Game User WebSocket does not exist")
        
        self.game_connections[game_name].pop(user_name)

        if len(self.game_connections[game_name]) == 0:
            self.game_connections.pop(game_name)

    async def close_game_connections(self, game_name: str):
        if game_name not in self.game_connections:
            raise Exception("Game does not exist")
        
        for user_name, connection in self.game_connections[game_name].items():
            await connection.close()
            self.game_connections[game_name].pop(user_name)

        self.game_connections.pop(game_name)

    async def send_message_to_game_user(self, game_name: str, user_name: str, message: str):
        if game_name not in self.game_connections:
            raise Exception("Game does not exist")

        if user_name not in self.game_connections[game_name]:
            raise Exception("Game User WebSocket does not exist")

        connection = self.game_connections[game_name][user_name]
        await connection.send_text(message)

    async def game_user_connection_sleep(self, game_name: str, user_name: str):
        if game_name not in self.game_connections:
            raise Exception("Game does not exist")

        if user_name not in self.game_connections[game_name]:
            raise Exception("Game User WebSocket does not exist")

        connection = self.game_connections[game_name][user_name]
        await connection.receive_text()

    async def broadcast_to_game(self, game_name: str, message: str):
        if game_name not in self.game_connections:
            raise Exception("Game does not exist")

        for connection in self.game_connections[game_name].values():
            await connection.send_text(message)	