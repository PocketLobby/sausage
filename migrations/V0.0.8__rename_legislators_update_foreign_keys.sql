-- See docs in V0.0.7. This is step three
BEGIN TRANSACTION;

ALTER TABLE representatives RENAME TO representatives_old;
ALTER TABLE legislators_new RENAME TO representatives;

ALTER TABLE votes
    DROP CONSTRAINT fk_votes_person_bioguide_id,
    ADD CONSTRAINT fk_votes_person_bioguide_id FOREIGN KEY (person_bioguide_id) REFERENCES representatives(bioguide_id);

COMMIT TRANSACTION;