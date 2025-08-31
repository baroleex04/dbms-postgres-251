-- Create View
DROP VIEW IF EXISTS trips_per_month;

CREATE VIEW trips_per_month AS
SELECT DATE_TRUNC('month', started_at) AS month, COUNT(*) AS total_trips
FROM trips
GROUP BY 1;

SELECT * FROM trips_per_month ORDER BY month DESC;

-- Create Materialized View
DROP MATERIALIZED VIEW IF EXISTS member_stats;
CREATE MATERIALIZED VIEW member_stats AS
SELECT DATE_TRUNC('month', started_at) AS month, COUNT(*) AS total_trips
FROM trips
GROUP BY 1;

SELECT * FROM member_stats ORDER BY month DESC;

-- Insert operations to show the difference in behavior between View and MV
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

-- Before Refresh
SELECT * FROM trips_per_month ORDER BY month DESC;
SELECT * FROM member_stats ORDER BY month DESC;

-- Refresh
REFRESH MATERIALIZED VIEW member_stats;

-- After Refresh
SELECT * FROM member_stats ORDER BY month DESC;

DELETE FROM trips WHERE DATE(started_at) = '2025-08-31';
