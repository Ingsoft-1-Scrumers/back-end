from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.lobby_connections: dict[str, list[WebSocket]] = {}
        
    async def lobby_connect(self, websocket: WebSocket, lobby_name: str):
        if lobby_name not in self.lobby_connections:
            self.lobby_connections[lobby_name] = []
        self.lobby_connections[lobby_name].append(websocket)

    async def lobby_disconnect(self, websocket: WebSocket, lobby_name: str):
        self.lobby_connections[lobby_name].remove(websocket)
    
    async def broadcast_to_lobby(self, lobby_name: str, message: str):
        for connection in self.lobby_connections[lobby_name]:
            await connection.send_text(message)

    


