from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.lobby_connections: dict[str, list[WebSocket]] = {}
        
    async def lobby_connect(self, websocket: WebSocket, lobby_name: str):
        await websocket.accept()
        if lobby_name not in self.lobby_connections:
            self.lobby_connections[lobby_name] = []
        self.lobby_connections[lobby_name].append(websocket)

    async def broadcast_to_lobby(self, lobby_name: str, message: str):
        if lobby_name in self.lobby_connections:
            for connection in self.lobby_connections[lobby_name]:
                await connection.send_text(message)

    def lobby_disconnect(self, websocket: WebSocket, lobby_name: str):
        self.lobby_connections[lobby_name].remove(websocket)
        if len(self.lobby_connections[lobby_name]) == 0:
            del self.lobby_connections[lobby_name]
    
    async def send_text_to_user(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def receive_text_from_user(self, websocket: WebSocket) -> str:
        return await websocket.receive_text()