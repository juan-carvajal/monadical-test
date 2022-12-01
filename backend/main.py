from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.engine import SessionLocal
from services.game.exceptions import MoveIntegrityException
from services.game.schemas import GameTile, Game, PlayerMove
from services.game.service import create_game, get_free_games, play_move, register_for_game, manager, map_move
from fastapi import (
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = [
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        for connection in self.active_connections:
            await connection.send_text(message)


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


@app.post("/games")
async def post_game(game: Game, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    game.host = token
    res = create_game(db, game)
    await manager.register_game(res.game_id, token)
    return res


@app.get("/games")
async def get_game(db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    return get_free_games(db)


@app.post("/games/{game_id}/membership")
async def join_game(game_id: int, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    row = register_for_game(db, game_id, token)
    if(row is None):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Could not join game"},
        )
    await manager.add_enemy_to_game(token, game_id)
    return row


@app.post("/games/{game_id}/moves")
async def move_game(move: PlayerMove, game_id: int, db: Session = Depends(get_db), token: str = Depends(get_token_http)):
    if(not manager.can_move(token, game_id)):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Is not {token}'s turn"},
        )
    res = play_move(db, move,game_id,token)
    if(res is None):
        return None
    turn = await manager.set_turn(game_id)
    res["turn"] = turn
    await manager.broadcast_game_update(res, game_id)
    return res


@app.get("/games/{game_id}/valid-moves")
def get_valid_moves_handler(game_id: int,move: PlayerMove, db: Session = Depends(get_db)):
    return map_move(db,game_id,move)


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, token: str = Depends(get_token_ws)):
    try:
        connected = await manager.connect(token, game_id, websocket)
        if (connected):
            await websocket.receive_text()
        else:
            raise WebSocketException(code=status.WS_1006_ABNORMAL_CLOSURE)
    except WebSocketDisconnect:
        await manager.disconnect(token, game_id, websocket)
