-- NOTE: Flyway changed the default table for tracking history to flyway_schema_history in version 5
-- ALTER TABLE schema_version RENAME TO flyway_schema_history;

-- Steps:
-- run this migration: flyway migrate -target=0.0.7 -configFiles=pocketlobby-fw.conf
-- load the data: ENV=production python -m utilities.import_legislators import_legislators.py
-- run v0.0.8 migration flyway migrate -target=0.0.8 -configFiles=pocketlobby-fw.conf

CREATE TABLE IF NOT EXISTS legislators_new (
  bioguide_id VARCHAR(20) PRIMARY KEY
  , lis_id VARCHAR(20) NULL UNIQUE
  , first_name TEXT NOT NULL
  , last_name TEXT NOT NULL
  , type varchar(5) NOT NULL
  , party TEXT NOT NULL
  , state VARCHAR(2) NOT NULL
  , district SMALLINT
)