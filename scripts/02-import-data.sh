#!/bin/bash
set -e

DB_NAME="app"
DB_USER="appuser"
CSV_DIR="/docker-entrypoint-initdb.d/source"
TABLE_NAME="app"

echo "Starting bulk CSV import into table: $TABLE_NAME..."

for csv_file in "$CSV_DIR"/*.csv; do
  if [ ! -f "$csv_file" ]; then
    echo "No CSV files found in $CSV_DIR. Skipping import."
    break
  fi

  echo "Importing $csv_file into $TABLE_NAME..."

  psql -v ON_ERROR_STOP=1 --username "$DB_USER" --dbname "$DB_NAME" \
    -c "\copy \"$TABLE_NAME\" FROM '$csv_file' WITH (FORMAT CSV, HEADER TRUE);"

  echo "Successfully imported $csv_file"
done

echo "All CSV files imported into $TABLE_NAME."