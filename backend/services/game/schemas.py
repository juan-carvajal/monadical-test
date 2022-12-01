from pydantic import BaseModel
from enum import Enum


class GameTile(BaseModel):
    game_id: int
    game_width: int
    game_height: int
    x: int
    y: int
    value: str

    class Config:
        orm_mode = True


class Game(BaseModel):
    game_id: int | None
    width: int
    height: int
    line_target: int
    tiles: list[GameTile] | None
    host: str | None
    enemy: str | None

    class Config:
        orm_mode = True


class Coordinate(BaseModel):
    x: int
    y: int


class PlayDirectionEnum(str, Enum):
    left = 'left'
    right = 'right'


class PlayerMove(BaseModel):
    row: int
    direction: PlayDirectionEnum
