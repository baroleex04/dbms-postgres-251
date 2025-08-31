ALTER TABLE trips DROP COLUMN IF EXISTS metadata;
ALTER TABLE trips ADD COLUMN metadata JSONB;

UPDATE trips 
SET metadata = '{"weather":"sunny","temperature":30}'
WHERE ride_id = '62D824C167C5384E';

SELECT ride_id, metadata AS weather
FROM trips
WHERE metadata->>'weather' = 'sunny';

SELECT * FROM trips;