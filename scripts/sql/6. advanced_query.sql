-- Window Function
SELECT ride_id, started_at::date AS day,
       ended_at - started_at AS duration,
       RANK() OVER (PARTITION BY started_at::date ORDER BY ended_at - started_at DESC) AS rank
FROM trips
WHERE started_at IS NOT NULL
LIMIT 10;


-- Recursive query
WITH RECURSIVE trip_chain AS (
    SELECT ride_id, start_station_name, end_station_name
    FROM trips
	WHERE ride_id = '62D824C167C5384E'
    UNION
    SELECT t.ride_id, t.start_station_name, t.end_station_name
    FROM trips t
    INNER JOIN trip_chain c ON t.start_station_name = c.end_station_name
)
SELECT * FROM trip_chain;