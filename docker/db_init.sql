CREATE DATABASE endorser;
CREATE USER endorseradminuser PASSWORD 'endorseradminPass';
CREATE USER endorseruser PASSWORD 'endorserPass';
ALTER DATABASE endorser OWNER TO endorseradminuser;
\connect endorser
CREATE EXTENSION IF NOT EXISTS pgcrypto;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO endorseradminuser;
GRANT USAGE ON SCHEMA public TO endorseruser;
GRANT ALL ON SCHEMA public TO endorseradminuser;
ALTER DEFAULT PRIVILEGES FOR USER endorseradminuser IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO endorseruser;
ALTER DEFAULT PRIVILEGES FOR USER endorseradminuser IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO endorseruser;
ALTER DEFAULT PRIVILEGES FOR USER endorseradminuser IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO endorseruser;
