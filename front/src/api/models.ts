export interface Game {
  game_id?: number
  width: number
  height: number
  line_target: number
  host?: string
  enemy?: string
}


export type GameStreamDataBoardRow = (string | null)[];

export interface GameStreamData {
  board: GameStreamDataBoardRow[];
  winner?: string;
  turn?: string;
}

export interface PlayerMove {
  row: number
  direction: 'right' | 'left'
}
