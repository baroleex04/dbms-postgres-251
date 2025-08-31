# dbms-postgres-251

## Run command
```
docker compose up -d
```

## Access the container and use database `bikedb`
```
 docker exec -it pg_container psql -U postgres -d bikedb
```

### Import data into PostgreSQL container
In CLI: Run queries in file `0.create_table.sql` (located in `scripts/sql/`)

### Query data and functionality testing
- Go to your browser, paste the URL `localhost:8082` to access the `pgadmin` - a UI for easy monitoring and testing Postgre database system properties.
- Testing queries are located in folder `scripts/sql`, with each file represents a functionality in Postgre DBS.

## Shutdown command
```
docker compose down -v
<!-- sudo rm -rf data -->
```