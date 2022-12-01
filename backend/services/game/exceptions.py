from services.game.schemas import PlayerMove

class MoveIntegrityException(Exception):
    def __init__(self, move : PlayerMove):
        self.move = move
        self.message = f"Provide move broke game integrity rules"
        super().__init__(self.message)

class GameNotFound(Exception):
    def __init__(self, game_id: int):
        self.game_id = game_id
        self.message = f"Provide game was not found"
        super().__init__(self.message)

class GameFullException(Exception):
    def __init__(self, game_id: int):
        self.game_id = game_id
        self.message = f"Provide game is already full"
        super().__init__(self.message)