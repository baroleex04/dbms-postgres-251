ALTER TABLE trips 
ADD CONSTRAINT chk_time CHECK (ended_at + INTERVAL '1 hour' >= started_at);

-- Valid
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

-- Invalid
INSERT INTO trips VALUES (
	'RIDE123456',
    'electric_bike',
    '2025-08-31 11:00:00',
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

DELETE FROM trips WHERE DATE(started_at) = '2025-08-31';

ALTER TABLE trips
DROP CONSTRAINT chk_time;