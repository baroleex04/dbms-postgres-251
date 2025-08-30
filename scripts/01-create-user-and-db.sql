-- Create a new, dedicated user for your application (not the superuser)
CREATE USER appuser WITH PASSWORD 'password';

-- Create a new, dedicated database for your application
CREATE DATABASE app;

-- Grant all privileges on the new database to the new user
GRANT ALL PRIVILEGES ON DATABASE app TO appuser;

-- Connect to the new database to set up objects within it
\c app;

GRANT ALL ON SCHEMA public TO appuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO appuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO appuser;
GRANT pg_read_server_files TO appuser;