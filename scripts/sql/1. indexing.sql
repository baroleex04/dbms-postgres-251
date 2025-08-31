-- Before indexing
SELECT * FROM trips WHERE start_station_id = '403';

EXPLAIN ANALYZE
SELECT * FROM trips WHERE start_station_id = '403';

-- Create index
CREATE INDEX idx_start_station ON trips(start_station_id);

-- After indexing
SELECT * FROM trips WHERE start_station_id = '403';

EXPLAIN ANALYZE
SELECT * FROM trips WHERE start_station_id = '403';
