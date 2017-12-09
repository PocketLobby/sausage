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
