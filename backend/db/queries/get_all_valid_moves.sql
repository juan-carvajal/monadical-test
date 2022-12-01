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
    generate_series AS num 
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
left_moves AS (
  SELECT 
    r.num AS x, 
    'left' as type, 
    CASE WHEN (
      MIN(t.y) -1
    ) IS NULL THEN (
      SELECT 
        width 
      FROM 
        gamec
    ) -1 ELSE (
      MIN(t.y) -1
    ) END y 
  FROM 
    all_rows r FULL 
    JOIN tiles t ON r.num = t.x 
  GROUP BY 
    t.x, 
    num
), 
right_moves AS (
  SELECT 
    r.num AS x, 
    'right' as type, 
    CASE WHEN (
      MAX(t.y) + 1
    ) IS NULL THEN 0 ELSE (
      MAX(t.y) + 1
    ) END y 
  FROM 
    all_rows r FULL 
    JOIN tiles t ON r.num = t.x 
  GROUP BY 
    t.x, 
    num
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
