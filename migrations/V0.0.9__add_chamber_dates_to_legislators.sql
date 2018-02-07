-- See notes in utilities/import_legislators.py. There are a lot of cases not covered with this schema
ALTER TABLE representatives
    ADD COLUMN chamber_begin_dt DATE NOT NULL DEFAULT '2900-12-31'
  , ADD COLUMN chamber_end_dt DATE NOT NULL DEFAULT '2900-12-31'