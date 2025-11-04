from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI(title="Communication Service")

# Lista de conexiones activas
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


@app.websocket("/api/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    #Canal de chat en tiempo real
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Nuevo mensaje: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/ws/health")
def root():
    return {"message": "Communication Service is online"}
