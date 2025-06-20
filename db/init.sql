CREATE USER psp_admin WITH PASSWORD 'psp';
CREATE DATABASE demo_project OWNER psp_admin;
GRANT ALL PRIVILEGES ON DATABASE demo_project TO psp_admin;