BEGIN;
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
-- Identify some errors
ROLLBACK;

-- Agree with change
COMMIT;

-- Testing
SELECT COUNT(*) FROM trips;