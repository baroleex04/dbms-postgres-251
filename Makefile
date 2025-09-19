# Variables
DB_CONTAINER=pg_container
DB_NAME=bikedb
DB_USER=postgres
SQL_FILE=./scripts/sql/init_schema.sql
ETL_SERVICE=etl
ETL_SCRIPT=scripts/etl/import_reports.py

.PHONY: up down init-db etl install-deps psql

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down -v

# Initialize schema (runs SQL script inside container)
init-db:
	docker exec -it $(DB_CONTAINER) \
		psql -U $(DB_USER) -d $(DB_NAME) -f /scripts/sql/init_schema.sql

# Run ETL job locally
etl:
	source .venv/bin/activate && \
	python3 $(ETL_SCRIPT)

# Install Python dependencies locally
setup-etl:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r scripts/etl/requirements.txt

# Open interactive psql shell
psql:
	docker exec -it $(DB_CONTAINER) \
		psql -U $(DB_USER) -d $(DB_NAME)
