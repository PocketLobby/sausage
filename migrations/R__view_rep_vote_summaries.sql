DROP VIEW vw_rep_vote_summaries CASCADE ; -- ALSO DROPS vw_cons_reps_vote_matches which is why it is here
CREATE VIEW vw_rep_vote_summaries AS
SELECT b.bill_id,
    b.house_passage_type,
    v.vote,
    reps.bioguide_id,
    reps.first_name,
    reps.last_name,
    reps.type,
    reps.state,
    reps.district
   FROM bills b
     JOIN votes v ON v.vote_id::text = b.most_recent_house_vote_id::text
     JOIN representatives reps ON v.person_bioguide_id::text = reps.bioguide_id
  WHERE b.most_recent_house_vote_id IS NOT NULL AND b.house_passage_type = 'rc'::passage_type
UNION
 SELECT b.bill_id,
    b.senate_passage_type AS house_passage_type,
    v.vote,
    reps.bioguide_id,
    reps.first_name,
    reps.last_name,
    reps.type,
    reps.state,
    reps.district
   FROM bills b
     JOIN votes v ON v.vote_id::text = b.most_recent_senate_vote_id::text
     JOIN representatives reps ON v.person_bioguide_id::text = reps.bioguide_id
  WHERE b.most_recent_senate_vote_id IS NOT NULL AND b.senate_passage_type = 'rc'::passage_type
UNION
 SELECT b.bill_id,
    b.house_passage_type,
    'for'::vote_type AS vote,
    reps.bioguide_id,
    reps.first_name,
    reps.last_name,
    reps.type,
    reps.state,
    reps.district
   FROM bills b
     JOIN representatives reps ON reps.type = 'rep'::text
  WHERE b.house_passage_type = ANY (ARRAY['vv'::passage_type, 'uc'::passage_type])
UNION
 SELECT b.bill_id,
    b.senate_passage_type AS house_passage_type,
    'for'::vote_type AS vote,
    reps.bioguide_id,
    reps.first_name,
    reps.last_name,
    reps.type,
    reps.state,
    -1 AS district
   FROM bills b
     JOIN representatives reps ON reps.type = 'sen'::text
  WHERE b.senate_passage_type = ANY (ARRAY['vv'::passage_type, 'uc'::passage_type]);
;
-- Matches every constituent vote with every legislator vote
-- This will get out of hand when we have lots of constituents (It will scale
-- by N * 546 representatives * Y votes)
-- should be unique on bill_id, legislator and constituent
CREATE VIEW vw_cons_reps_vote_matches AS
  WITH cons_with_legs AS (
      SELECT
        cons.id
        , representatives.bioguide_id
        , representatives.type
      FROM constituents as cons
        JOIN representatives ON TRUE
  )
  SELECT
      cwl.id as constituent_id
    , cwl.bioguide_id
    , b.bill_id
    , vb.vote AS leg_vote
    , cv.vote AS cons_vote
    , cv.vote = 'abstain' OR vb.vote = 'abstain' as either_abstain_bool
    , cv.vote = vb.vote as cons_leg_vote_match_bool
  FROM cons_with_legs AS cwl
    JOIN bills AS b ON TRUE
    LEFT JOIN vw_rep_vote_summaries AS vb ON vb.bioguide_id = cwl.bioguide_id AND vb.bill_id = b.bill_id
    LEFT JOIN user_votes AS cv ON cv.constituent_id = cwl.id AND cv.bill_id = b.id
;
