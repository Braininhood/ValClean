-- SQL script to create PostgreSQL database and user for VALClean project
-- Run this script as PostgreSQL superuser (usually 'postgres')

-- Create user if not exists (PostgreSQL doesn't support IF NOT EXISTS for users)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'valclean_user') THEN
        CREATE USER valclean_user WITH PASSWORD 'valclean_pass';
    ELSE
        ALTER USER valclean_user WITH PASSWORD 'valclean_pass';
    END IF;
END
$$;

-- Drop database if exists (use with caution!)
DROP DATABASE IF EXISTS valclean_db;

-- Create database
CREATE DATABASE valclean_db OWNER valclean_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE valclean_db TO valclean_user;

-- Connect to the new database and grant schema privileges
\c valclean_db
GRANT ALL ON SCHEMA public TO valclean_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO valclean_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO valclean_user;
