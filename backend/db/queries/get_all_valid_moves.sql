WITH gamec AS (
  SELECT 
    * 
  FROM 
    game 
  WHERE 
    game_id = :game_id
), 
tiles AS (
  SELECT 
    * 
  FROM 
    game_tile 
  WHERE 
    game_id = (
      SELECT 
        game_id 
      FROM 
        gamec
    )
), 
all_rows AS (
  SELECT 
    generate_series AS row 
  FROM 
    generate_series(
      0, 
      (
        SELECT 
          height 
        FROM 
          gamec
      ) -1
    )
),
all_cols AS (
  SELECT 
    generate_series AS col 
  FROM 
    generate_series(
      0, 
      (
        SELECT 
          width 
        FROM 
          gamec
      ) -1
    )
),
available_moves AS(
  SELECT row as x,col as y from all_rows r cross join all_cols c 
    full JOIN tiles t ON r.row = t.x and c.col = t.y where value is null
),
left_moves AS (
  SELECT 
    r.row AS x, 
    'left' as type, 
    MAX(m.y) y 
  FROM 
    all_rows r FULL 
    JOIN available_moves m ON r.row = m.x 
  GROUP BY 
    m.x, 
    row
), 
right_moves AS (
  SELECT 
    r.row AS x, 
    'right' as type, 
    MIN(m.y) y 
  FROM 
    all_rows r FULL 
    JOIN available_moves m ON r.row = m.x 
  GROUP BY 
    m.x, 
    row
), 
all_moves AS (
  SELECT 
    * 
  FROM 
    right_moves 
  WHERE 
    y < (
      SELECT 
        width 
      FROM 
        gamec
    ) 
  UNION 
  SELECT 
    * 
  FROM 
    left_moves 
  WHERE 
    y >= 0
), 
mapped_move as(
  select 
    to_json(all_moves) 
  from 
    all_moves 
  where 
    type = :direction 
    and x = :row
  limit 
    1
),
game_json as(
	  select 
    to_json(gamec) 
  from 
    gamec 
  limit 
    1
)
SELECT 
  json_build_object(
    'valid_moves', 
    COALESCE(
      json_agg(distinct all_moves), 
      '[]' :: json
    ), 
    'mapped_move', 
    (
      select 
        * 
      from 
        mapped_move
    ),
	'game',
	(
      select 
        * 
      from 
        game_json
    )
  ) as result 
FROM 
  all_moves
