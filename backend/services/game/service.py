from sqlalchemy.orm import Session
from services.game.exceptions import GameNotFound, MoveIntegrityException

from services.game.models import Game, GameTile
from services.game.schemas import GameTile as GTSchema
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

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
