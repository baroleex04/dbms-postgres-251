# Variables
DB_CONTAINER=pg_container
DB_NAME=bikedb
DB_USER=postgres
SQL_FILE=./scripts/sql/init_schema.sql
ETL_SERVICE=etl
ETL_REPORT_SCRIPT=scripts/etl/import_reports.py
ETL_MRI_SCRIPT=scripts/etl/import_mri_data.py

.PHONY: up down init-db etl-report etl-mri install-deps psql

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

# Run ETL report job locally
etl-report:
	source .venv/bin/activate && \
	python3 $(ETL_REPORT_SCRIPT)

clear-report:
	docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME) -c "\
	TRUNCATE TABLE findings, spine_levels, extra_findings, reports RESTART IDENTITY CASCADE; \
	"

# Run ETL job locally
etl-mri:
	source .venv/bin/activate && \
	python3 $(ETL_MRI_SCRIPT)

clear-mri:
	docker exec -it $(DB_CONTAINER) \
		psql -U $(DB_USER) -d $(DB_NAME) -c "TRUNCATE TABLE dicom_metadata RESTART IDENTITY CASCADE;"

# Install Python dependencies locally
setup-etl:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r scripts/etl/requirements.txt

# Open interactive psql shell
psql:
	docker exec -it $(DB_CONTAINER) \
		psql -U $(DB_USER) -d $(DB_NAME)
