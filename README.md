# dbms-postgres-251

## Run command
```
docker compose up -d
```

## Shutdown command
```
docker compose down -v
sudo rm -rf data
```

## Connection command to database
```
psql -h localhost -p 5432 -U appuser -d app
```