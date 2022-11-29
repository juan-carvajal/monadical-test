from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session

from db.engine import SessionLocal
from services.game.exceptions import MoveIntegrityException
from services.game.schemas import GameTile, Game
from services.game.service import create_game, get_free_games, play_move, register_for_game
from fastapi import (
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print(len(self.active_connections))
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def get_token_ws(
    token: str | None = Query(default=None),
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return token


async def get_token_http(
    token: str | None = Query(default=None),
):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


@app.exception_handler(MoveIntegrityException)
async def unicorn_exception_handler(request: Request, exc: MoveIntegrityException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message, "details": exc.move.dict()},
    )


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/test")
async def get_test(move: GameTile, db: Session = Depends(get_db)):
    return play_move(db, move)


@app.post("/games")
async def post_game(game: Game, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    game.host = token
    return create_game(db, game)


@app.get("/games")
async def get_game(db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    return get_free_games(db)


@app.post("/games/{game_id}/membership")
async def join_game(game_id: int, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    return register_for_game(db, game_id, token)


@app.post("/games/{game_id}/moves")
async def move_game(move: GameTile, game_id: int, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    move.value = token
    move.game_id = game_id
    return play_move(db, move)


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, token: str = Depends(get_token_ws)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{game_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{game_id} left the chat")
