from sqlalchemy.orm import Session
from services.game.exceptions import GameFullException, GameNotFound, MoveIntegrityException

from services.game.models import Game, GameTile
from services.game.schemas import GameTile as GTSchema,Game as GameSchema
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update

from services.game.utils import check_grid


def get_game(db: Session, game_id: int):
    return db.query(Game).filter(Game.game_id == game_id).first()


def get_all_tiles(db: Session, game_id: int):
    return db.query(GameTile).filter(GameTile.game_id == game_id).all()


def check_win(db: Session, last_play: GTSchema):
    game = get_game(db, last_play.game_id)
    if (game is None):
        raise GameNotFound(last_play.game_id)
    tiles = [[None]*(game.height) for _ in range(game.width)]
    for tile in game.tiles:
        tiles[tile.x][tile.y] = tile.value
    return tiles, check_grid(tiles, game.line_target, last_play.value, last_play.x, last_play.y)

# play_move checks if the current move wins the game
# first elem in tuple is true if the player wins with the current move, the second indicates if the passed move was applied
def play_move(db: Session, value: GTSchema):
    try:
        stmt = insert(GameTile).values(
            [value.dict()]).on_conflict_do_nothing().returning(GameTile)
        result = db.execute(stmt)
        r = result.first()
        if (r is None):
            # This means there was no update. The move was a duplicate
            return None
        return check_win(db, value)
    except IntegrityError:
        raise MoveIntegrityException(value)

def get_free_games(db: Session):
    return db.query(Game).filter(Game.enemy is None).all()

def create_game(db: Session, game_schema: GameSchema):
    db_game = Game(host=game_schema.host,width=game_schema.width,height=game_schema.height,line_target=game_schema.line_target)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def register_for_game(db: Session,game_id:int, player_id: str):
    game = get_game(db,game_id)
    if (game is None):
        raise GameNotFound(game_id)
    if (game.enemy is not None):
        raise GameFullException(game_id)
    return db.execute(update(Game).where(Game.game_id == game_id).values(enemy=player_id).returning(Game)).first()