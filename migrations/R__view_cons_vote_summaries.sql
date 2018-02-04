DROP VIEW vw_cons_vote_summaries;
CREATE VIEW vw_cons_vote_summaries AS
   SELECT b.bill_id,
    v.vote,
    cons.id,
    cons.email,
    cons.first_name,
    cons.last_name,
    cons.zip_code,
    cons.user_token,
    cons.pledge_amount,
    cons.venmo_id,
    cons.state,
    cons.district
   FROM bills b
     JOIN user_votes v ON v.bill_id = b.id
     JOIN constituents cons ON cons.id = v.constituent_id;
