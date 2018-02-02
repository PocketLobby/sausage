DROP VIEW vw_cons_reps;
CREATE VIEW vw_cons_reps AS
  SELECT cons.id,
    cons.email,
    cons.first_name AS cons_first_name,
    cons.last_name AS cons_last_name,
    cons.user_token,
    cons.pledge_amount,
    cons.venmo_id,
    reps.bioguide_id,
    reps.first_name AS rep_first_name,
    reps.last_name AS rep_last_name,
    reps.state AS rep_state,
    reps.district AS rep_district,
    reps.type
  FROM constituents cons
    JOIN representatives reps ON reps.state = cons.state AND
         -- The house of representatives case
         (COALESCE(reps.district::integer, '-1'::integer) = cons.district OR
         -- The senate case
          COALESCE(reps.district::integer, '-1'::integer) = '-1'::integer);
