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
    game_id: int
    width: int
    height: int
    line_target: int
    tiles: list[GameTile]

    class Config:
        orm_mode = True
