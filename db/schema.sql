SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: token_origin; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.token_origin AS ENUM (
    'twitch',
    'spotify'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: application_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.application_user (
    id integer NOT NULL,
    external_user_id character varying NOT NULL,
    username character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: application_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.application_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: application_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.application_user_id_seq OWNED BY public.application_user.id;


--
-- Name: authorization_token; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.authorization_token (
    id integer NOT NULL,
    user_id integer,
    origin public.token_origin,
    access_token character varying NOT NULL,
    refresh_token character varying NOT NULL,
    invalid_token boolean DEFAULT false,
    expires_at timestamp with time zone
);


--
-- Name: authorization_token_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.authorization_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: authorization_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.authorization_token_id_seq OWNED BY public.authorization_token.id;


--
-- Name: refresh_token; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_token (
    id integer NOT NULL,
    user_id integer,
    refresh_token character varying NOT NULL,
    refresh_token_hash character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    invalidated_at timestamp with time zone
);


--
-- Name: refresh_token_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.refresh_token_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refresh_token_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.refresh_token_id_seq OWNED BY public.refresh_token.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: application_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user ALTER COLUMN id SET DEFAULT nextval('public.application_user_id_seq'::regclass);


--
-- Name: authorization_token id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token ALTER COLUMN id SET DEFAULT nextval('public.authorization_token_id_seq'::regclass);


--
-- Name: refresh_token id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_token ALTER COLUMN id SET DEFAULT nextval('public.refresh_token_id_seq'::regclass);


--
-- Name: application_user application_user_external_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user
    ADD CONSTRAINT application_user_external_user_id_key UNIQUE (external_user_id);


--
-- Name: application_user application_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user
    ADD CONSTRAINT application_user_pkey PRIMARY KEY (id);


--
-- Name: authorization_token authorization_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token
    ADD CONSTRAINT authorization_token_pkey PRIMARY KEY (id);


--
-- Name: refresh_token refresh_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_token
    ADD CONSTRAINT refresh_token_pkey PRIMARY KEY (id);


--
-- Name: refresh_token refresh_token_refresh_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_token
    ADD CONSTRAINT refresh_token_refresh_token_hash_key UNIQUE (refresh_token_hash);


--
-- Name: refresh_token refresh_token_refresh_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_token
    ADD CONSTRAINT refresh_token_refresh_token_key UNIQUE (refresh_token);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: authorization_token authorization_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token
    ADD CONSTRAINT authorization_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.application_user(id) ON DELETE CASCADE;


--
-- Name: refresh_token refresh_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_token
    ADD CONSTRAINT refresh_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.application_user(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20240211001319');
