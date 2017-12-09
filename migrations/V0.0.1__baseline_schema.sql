--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.3
-- Dumped by pg_dump version 10.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: passage_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE passage_type AS ENUM (
    'vv',
    'uc',
    'rc'
);


--
-- Name: vote_type; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE vote_type AS ENUM (
    'for',
    'against',
    'abstain',
    'present'
);


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bill_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE bill_votes (
    id integer NOT NULL,
    bill_type character varying(20),
    chamber character varying(3),
    congressional_session integer,
    vote_dttm timestamp without time zone,
    vote_cnt integer,
    passage_requirement numeric,
    result character varying(20),
    congress integer,
    source_url text,
    updated_dttm timestamp without time zone,
    vote_id character varying(20),
    yea_vote_cnt integer,
    nay_vote_cnt integer,
    abstain_vote_cnt integer,
    present_vote_cnt integer
);


--
-- Name: bills; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE bills (
    id integer NOT NULL,
    bill_id character varying(20) NOT NULL,
    active boolean NOT NULL,
    passed_house_bool boolean DEFAULT false NOT NULL,
    house_passage_type passage_type,
    most_recent_house_vote_id character varying(20),
    passed_house_dttm timestamp without time zone,
    passed_senate_bool boolean DEFAULT false NOT NULL,
    senate_passage_type passage_type,
    most_recent_senate_vote_id character varying(20),
    passed_senate_dttm timestamp without time zone
);


--
-- Name: bills_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE bills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE bills_id_seq OWNED BY bill_votes.id;


--
-- Name: bills_old; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE bills_old (
    id integer NOT NULL,
    bill_id character varying(20) NOT NULL,
    congressional_session integer,
    passed_house_bool boolean DEFAULT false NOT NULL,
    house_passage_type passage_type,
    house_vote_id character varying(20),
    passed_senate_bool boolean DEFAULT false NOT NULL,
    senate_passage_type passage_type,
    senate_vote_id character varying(20)
);


--
-- Name: bills_id_seq1; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE bills_id_seq1
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bills_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE bills_id_seq1 OWNED BY bills_old.id;


--
-- Name: bills_temp_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE bills_temp_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bills_temp_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE bills_temp_id_seq OWNED BY bills.id;


--
-- Name: constituents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE constituents (
    id integer NOT NULL,
    email character varying(200) NOT NULL,
    first_name character varying(200) NOT NULL,
    last_name character varying(200) NOT NULL,
    zip_code character varying(20) NOT NULL,
    user_token character varying(20) NOT NULL,
    pledge_amount numeric NOT NULL,
    venmo_id character varying(200) NOT NULL,
    state character varying(2),
    district integer
);


--
-- Name: representatives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE representatives (
    last_name text,
    first_name text,
    birthday text,
    gender text,
    type text,
    state text,
    district text,
    party text,
    url text,
    address text,
    phone text,
    contact_form text,
    rss_url text,
    twitter text,
    facebook text,
    youtube text,
    youtube_id text,
    bioguide_id text,
    thomas_id text,
    opensecrets_id text,
    lis_id text,
    cspan_id text,
    govtrack_id text,
    votesmart_id text,
    ballotpedia_id text,
    washington_post_id text,
    icpsr_id text,
    wikipedia_id text
);


--
-- Name: schema_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE schema_version (
    installed_rank integer NOT NULL,
    version character varying(50),
    description character varying(200) NOT NULL,
    type character varying(20) NOT NULL,
    script character varying(1000) NOT NULL,
    checksum integer,
    installed_by character varying(100) NOT NULL,
    installed_on timestamp without time zone DEFAULT now() NOT NULL,
    execution_time integer NOT NULL,
    success boolean NOT NULL
);


--
-- Name: user_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE user_votes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    bill_id integer NOT NULL,
    vote vote_type NOT NULL
);


--
-- Name: user_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE user_votes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE user_votes_id_seq OWNED BY user_votes.id;


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE users_id_seq OWNED BY constituents.id;


--
-- Name: votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE votes (
    id integer NOT NULL,
    vote_id character varying(20),
    person_bioguide_id character varying(20),
    vote vote_type
);


--
-- Name: votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE votes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE votes_id_seq OWNED BY votes.id;


--
-- Name: bill_votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY bill_votes ALTER COLUMN id SET DEFAULT nextval('bills_id_seq'::regclass);


--
-- Name: bills id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills ALTER COLUMN id SET DEFAULT nextval('bills_temp_id_seq'::regclass);


--
-- Name: bills_old id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills_old ALTER COLUMN id SET DEFAULT nextval('bills_id_seq1'::regclass);


--
-- Name: constituents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY constituents ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Name: user_votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_votes ALTER COLUMN id SET DEFAULT nextval('user_votes_id_seq'::regclass);


--
-- Name: votes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY votes ALTER COLUMN id SET DEFAULT nextval('votes_id_seq'::regclass);


--
-- Name: bill_votes bill_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bill_votes
    ADD CONSTRAINT bill_votes_pkey PRIMARY KEY (id);


--
-- Name: bills_old bills_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills_old
    ADD CONSTRAINT bills_pkey PRIMARY KEY (id);


--
-- Name: bills bills_temp_bill_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills
    ADD CONSTRAINT bills_temp_bill_id_key UNIQUE (bill_id);


--
-- Name: bills bills_temp_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills
    ADD CONSTRAINT bills_temp_pkey PRIMARY KEY (id);


--
-- Name: schema_version schema_version_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY schema_version
    ADD CONSTRAINT schema_version_pk PRIMARY KEY (installed_rank);


--
-- Name: user_votes user_votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_votes
    ADD CONSTRAINT user_votes_pkey PRIMARY KEY (id);


--
-- Name: constituents users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY constituents
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: votes votes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT votes_pkey PRIMARY KEY (id);


--
-- Name: bills_vote_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX bills_vote_id ON bill_votes USING btree (vote_id);


--
-- Name: idx_people_bioguide_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_people_bioguide_id ON representatives USING btree (bioguide_id);


--
-- Name: idx_user_votes_user_id_bill_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_user_votes_user_id_bill_id ON user_votes USING btree (user_id, bill_id);


--
-- Name: people_bioguided_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX people_bioguided_id ON representatives USING btree (bioguide_id);


--
-- Name: schema_version_s_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX schema_version_s_idx ON schema_version USING btree (success);


--
-- Name: votes_vote_id_person_bioguide_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX votes_vote_id_person_bioguide_id ON votes USING btree (vote_id, person_bioguide_id);


--
-- Name: bills_old fk_bills_bill_votes_1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills_old
    ADD CONSTRAINT fk_bills_bill_votes_1 FOREIGN KEY (house_vote_id) REFERENCES bill_votes(vote_id);


--
-- Name: bills_old fk_bills_bill_votes_2; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY bills_old
    ADD CONSTRAINT fk_bills_bill_votes_2 FOREIGN KEY (senate_vote_id) REFERENCES bill_votes(vote_id);


--
-- Name: user_votes fk_user_votes_bill_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_votes
    ADD CONSTRAINT fk_user_votes_bill_id FOREIGN KEY (bill_id) REFERENCES bills(id);


--
-- Name: user_votes fk_user_votes_people_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY user_votes
    ADD CONSTRAINT fk_user_votes_people_id FOREIGN KEY (user_id) REFERENCES constituents(id);


--
-- Name: votes fk_votes_bill_votes_1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT fk_votes_bill_votes_1 FOREIGN KEY (vote_id) REFERENCES bill_votes(vote_id);


--
-- Name: votes fk_votes_person_bioguide_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY votes
    ADD CONSTRAINT fk_votes_person_bioguide_id FOREIGN KEY (person_bioguide_id) REFERENCES representatives(bioguide_id);


--
-- PostgreSQL database dump complete
--

