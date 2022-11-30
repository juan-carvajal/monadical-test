WITH gamec AS
(
   SELECT
      * 
   FROM
      game 
   WHERE
      game_id = 19 
)
,
tiles AS 
(
   SELECT
      * 
   FROM
      game_tile 
   WHERE
      game_id = 
      (
         SELECT
            game_id 
         FROM
            gamec
      )
)
,
all_rows AS 
(
   SELECT
      generate_series AS num 
   FROM
      generate_series(0, 
      (
         SELECT
            height 
         FROM
            gamec
      )
       - 1) 
)
,
right_moves AS 
(
   SELECT
      r.num AS x,
      CASE
         WHEN
            (
               MIN(t.y) - 1
            )
            IS NULL 
         THEN
(
            SELECT
               width 
            FROM
               gamec) - 1 
            ELSE
(MIN(t.y) - 1) 
      END
      y 
            FROM
               all_rows r 
               FULL JOIN
                  tiles t 
                  ON r.num = t.x 
            GROUP BY
               t.x,
               num 
)
,
left_moves AS 
(
   SELECT
      r.num AS x,
      CASE
         WHEN
            (
               MAX(t.y) + 1
            )
            IS NULL 
         THEN
            0 
         ELSE
(MAX(t.y) + 1) 
      END
      y 
   FROM
      all_rows r 
      FULL JOIN
         tiles t 
         ON r.num = t.x 
   GROUP BY
      t.x, num 
)
, all_moves AS 
(
   SELECT
      * 
   FROM
      right_moves 
   WHERE
      y >= 0 
   UNION
   SELECT
      * 
   FROM
      left_moves 
   WHERE
      y < (
      SELECT
         width 
      FROM
         gamec) 
)
SELECT
   json_agg(all_moves)::jsonb 
FROM
   all_moves 
GROUP BY
   x,
   y