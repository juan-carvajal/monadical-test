from pydantic import BaseModel


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
    host: str  | None
    enemy: str | None

    class Config:
        orm_mode = True
