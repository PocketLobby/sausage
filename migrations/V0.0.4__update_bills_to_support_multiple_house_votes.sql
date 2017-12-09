ALTER TABLE bills RENAME COLUMN passed_house_dttm TO house_activity_dttm;
ALTER TABLE bills RENAME COLUMN passed_senate_dttm TO senate_activity_dttm;

ALTER TABLE user_votes RENAME COLUMN user_id TO constituent_id;
ALTER TABLE user_votes ADD COLUMN vote_collected_dttm TIMESTAMP NOT NULL DEFAULT '1900-01-01';
