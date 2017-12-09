CREATE TABLE transactional_emails (
    id SERIAL PRIMARY KEY
    , email_type TEXT NOT NULL
    , to_user_id INTEGER NOT NULL
    , to_email TEXT NOT NULL
    , sent_dttm TIMESTAMP
);
