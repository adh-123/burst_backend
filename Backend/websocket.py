from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):

        # ROOM CONNECTIONS
        self.active_connections = {}


    # CONNECT USER TO ROOM
    async def connect(
        self,
        websocket: WebSocket,
        room_id: int
    ):

        await websocket.accept()

        if room_id not in self.active_connections:

            self.active_connections[room_id] = []

        self.active_connections[room_id].append(
            websocket
        )


    # DISCONNECT USER
    def disconnect(
        self,
        websocket: WebSocket,
        room_id: int
    ):

        self.active_connections[room_id].remove(
            websocket
        )


    # SEND MESSAGE TO ROOM USERS ONLY
    async def broadcast(
        self,
        room_id: int,
        message: str
    ):

        for connection in self.active_connections.get(
            room_id,
            []
        ):

            await connection.send_text(
                message
            )


# MANAGER OBJECT
manager = ConnectionManager()