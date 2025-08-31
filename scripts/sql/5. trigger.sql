DROP TABLE IF EXISTS trip_logs;
DROP TRIGGER IF EXISTS after_trip_insert ON trips;
DROP FUNCTION IF EXISTS log_trip;

CREATE TABLE trip_logs(
   log_id SERIAL PRIMARY KEY,
   ride_id TEXT,
   created_at TIMESTAMP DEFAULT now()
);

CREATE OR REPLACE FUNCTION log_trip()
RETURNS TRIGGER AS $$
BEGIN
   INSERT INTO trip_logs(ride_id) VALUES (NEW.ride_id);
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_trip_insert
AFTER INSERT ON trips
FOR EACH ROW EXECUTE FUNCTION log_trip();

-- Check empty table
SELECT * FROM trip_logs;

INSERT INTO trips VALUES (
	'RIDE123456',
    'electric_bike',
    '2025-08-31 09:00:00',
    '2025-08-31 09:30:00',
    'Station A',
    'STA001',
    'Station B',
    'STB002',
    10.762622,
    106.660172,
    10.775659,
    106.700424,
    'member'
);

-- Table after triggering
SELECT * FROM trip_logs;

DELETE FROM trips WHERE DATE(started_at) = '2025-08-31';
