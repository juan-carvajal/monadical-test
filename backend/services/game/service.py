from sqlalchemy.orm import Session
from services.game.exceptions import GameFullException, GameNotFound, MoveIntegrityException

from services.game.models import Game, GameTile
from services.game.schemas import GameTile as GTSchema, Game as GameSchema, PlayerMove, PlayDirectionEnum, WSEvent
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update

from services.game.utils import check_grid
import json
from fastapi import WebSocket, status
import asyncio
from sqlalchemy.sql import text
from db.utils import get_raw_sql_query
import time
import random
from fastapi.responses import JSONResponse


class GameContext():
    def __init__(self, host: str, enemy: str | None = None):
        self.host = host
        self.enemy = enemy
        self.turn = host
        self.websockets: list[tuple[str, WebSocket]] = []

    def add_listener(self, player_id: str, ws: WebSocket):
        if(player_id != self.host and player_id != self.enemy):
            return

        self.websockets.append((player_id, ws))

    def can_join(self, player_id: str):
        return player_id == self.host or player_id == self.enemy

    async def broadcast_message(self, message: dict):
        str_message = json.dumps(message)
        for (_, ws) in self.websockets:
            await ws.send_text(str_message)

    def remove_listener(self, player_id: str, ws: WebSocket):
        self.websockets.remove((player_id, ws))


class GameManager:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.active_connections: dict[int, GameContext] = {}
        self.agents: dict[int, str] = {}

    async def register_new_ai_agent(self, game_id: int, player_id: str):
        async with self.lock:
            if(game_id in self.agents):
                return

            self.agents[game_id] = player_id

    async def move_ai(self, db: Session, game_id: int):
        async with self.lock:
            if(game_id not in self.agents):
                return None
            ai_id = self.agents[game_id]
            next_move = get_ai_move(db, game_id)
            move = random.choice(next_move)
            if(not self.can_move(ai_id, game_id)):
                raise Exception("TODO")
            res = play_move(db, move, game_id, ai_id)
            if(res is None):
                return None
            turn = self.__set_next_turn(game_id)
            res["turn"]=turn
            return res

    async def register_game(self, game_id: int, host: str):
        async with self.lock:
            if(game_id in self.active_connections):
                return

            self.active_connections[game_id] = GameContext(host)

    async def connect(self, player_id: str, game_id: int, ws: WebSocket):
        try:
            async with self.lock:
                if(game_id not in self.active_connections or not self.active_connections[game_id].can_join(player_id)):
                    return False

                await ws.accept()
                self.active_connections[game_id].add_listener(player_id, ws)
                return True
        except:
            return False

    def can_move(self, player_id: str, game_id: int):
        return game_id in self.active_connections and self.active_connections[game_id].turn == player_id and self.active_connections[game_id].enemy is not None

    def get_next_turn(self, game_id: int):
        if(game_id not in self.active_connections):
            return None

        if(self.active_connections[game_id].turn == self.active_connections[game_id].host and self.active_connections[game_id].enemy is None):
            return None

        return self.active_connections[game_id].host if self.active_connections[game_id].turn == self.active_connections[game_id].enemy else self.active_connections[game_id].enemy

    async def set_turn(self, game_id: int):
        async with self.lock:
            return self.__set_next_turn(game_id)

    def __set_next_turn(self, game_id: int):
        if(game_id not in self.active_connections):
            return None

        next_turn = self.get_next_turn(game_id)
        if (next_turn is None):
            return None

        self.active_connections[game_id].turn = next_turn
        return next_turn

    async def get_turn(self, game_id: int):
        async with self.lock:
            if(game_id not in self.active_connections):
                return None
            return self.active_connections[game_id].turn

    async def add_enemy_to_game(self, player_id: str, game_id: int):
        async with self.lock:
            if(game_id in self.active_connections and self.active_connections[game_id].host != player_id and self.active_connections[game_id].enemy is None):
                self.active_connections[game_id].enemy = player_id
                return

            raise GameFullException(game_id)

    async def disconnect(self, player_id: str, game_id: int, ws: WebSocket):
        async with self.lock:
            if(game_id not in self.active_connections):
                return
            self.active_connections[game_id].remove_listener(player_id, ws)

    async def broadcast_game_update(self, message: dict, game_id: int):
        async with self.lock:
            await self.__broadcast_game_update(message, game_id)

    async def __broadcast_game_update(self, message: dict, game_id: int):
        if(game_id not in self.active_connections):
            return
        await self.active_connections[game_id].broadcast_message(message)


manager = GameManager()


def map_move(db: Session, game_id: int, move: PlayerMove) -> dict:
    stmt = text(get_raw_sql_query('get_all_valid_moves.sql'))
    res = db.execute(
        stmt, {"game_id": game_id, "row": move.row, "direction": move.direction})
    for row, in res:
        return row
    return {}


def get_ai_move(db: Session, game_id: int) -> list[PlayerMove]:
    tiles, _ = get_current_board(db, game_id)
    valid_moves = []
    for rownum, row in enumerate(tiles):
        if(row[0] is None):
            valid_moves.append(PlayerMove(
                row=rownum, direction=PlayDirectionEnum.left))

        if(row[-1] is None):
            valid_moves.append(PlayerMove(
                row=rownum, direction=PlayDirectionEnum.right))

    return valid_moves


def get_game(db: Session, game_id: int):
    return db.query(Game).filter(Game.game_id == game_id).first()


def get_all_tiles(db: Session, game_id: int):
    return db.query(GameTile).filter(GameTile.game_id == game_id).all()


def get_current_board(db: Session, game_id: int):
    game = get_game(db, game_id)
    if (game is None):
        raise GameNotFound(game_id)
    tiles = [[None]*(game.height) for _ in range(game.width)]  # type: ignore
    for tile in game.tiles:
        tiles[tile.x][tile.y] = tile.value
    return tiles, game


async def get_current_game_status(db: Session, game_id: int):
    tiles, game = get_current_board(db, game_id)
    return {
        "board": tiles,
        "winner": game.winner,
        "turn": await manager.get_turn(game_id)
    }


def check_win(db: Session, last_play: GTSchema):
    game = get_game(db, last_play.game_id)
    if (game is None):
        raise GameNotFound(last_play.game_id)
    tiles = [[None]*(game.height) for _ in range(game.width)]  # type: ignore
    for tile in game.tiles:
        tiles[tile.x][tile.y] = tile.value
    return tiles, check_grid(tiles, game.line_target, last_play.value, last_play.x, last_play.y) # type: ignore

# play_move checks if the current move wins the game
# first elem in tuple is true if the player wins with the current move, the second indicates if the passed move was applied
def play_move(db: Session, value: PlayerMove, game_id: int, player_id: str):
    try:
        all_moves = map_move(db, game_id, value)
        mapped_move = all_moves.get("mapped_move")
        if(mapped_move is None):
            raise MoveIntegrityException(value)
        game = all_moves.get("game")
        if(game is None):
            raise GameNotFound(game_id)
        gt = GTSchema(game_id=game_id, game_height=game["height"], game_width=game["width"],
                      x=mapped_move["x"], y=mapped_move["y"], value=player_id)
        stmt = insert(GameTile).values(
            [gt.dict()]).on_conflict_do_nothing().returning(GameTile)
        result = db.execute(stmt)
        if (result.first() is None):
            raise MoveIntegrityException(value)

        board, (wins, _) = check_win(db, gt)
        if(wins):
            db.query(Game).filter(Game.game_id == game_id).update(
                {'winner': player_id})

        db.commit()
        return {
            "board": board,
            "winner": None if not wins else gt.value
        }
    except Exception as e:
        db.rollback()
        raise e


def get_free_games(db: Session, player_id: str):
    games = db.query(Game).filter((Game.enemy == None) | (
        Game.host == player_id) | (Game.enemy == player_id)).all()
    db.close()
    return list(filter(lambda x: x.game_id in manager.active_connections.keys(), games))


async def turn_game_into_ai(db: Session, game_id: int, player_id: str):
    game = get_game(db, game_id)
    if(game is None):
        raise Exception("TODO")
    if(game.host != player_id):
        raise Exception("TODO")
    if(game.enemy is not None):
        raise Exception("TODO")

    bot_user_name = f"bot_{int(time.time())}"

    row = register_for_game(db, game_id, bot_user_name)
    if(row is None):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Could not join game"},
        )
    await manager.add_enemy_to_game(bot_user_name, game_id)
    event = WSEvent(type="opponent", payload={"username": bot_user_name})
    await manager.broadcast_game_update(event.dict(), game_id)
    await manager.register_new_ai_agent(game_id, bot_user_name)
    return row


def create_game(db: Session, game_schema: GameSchema):
    db_game = Game(host=game_schema.host, width=game_schema.width,
                   height=game_schema.height, line_target=game_schema.line_target)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def register_for_game(db: Session, game_id: int, player_id: str) -> Game:
    game = get_game(db, game_id)
    if (game is None):
        raise GameNotFound(game_id)
    if (game.enemy is not None):
        raise GameFullException(game_id)
    res = db.execute(update(Game).where(Game.game_id == game_id).values(
        enemy=player_id).returning(Game)).first()
    db.commit()
    return res
