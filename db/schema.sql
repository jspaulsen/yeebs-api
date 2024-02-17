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
    user_id integer NOT NULL,
    external_user_id character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: application_user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.application_user_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: application_user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.application_user_user_id_seq OWNED BY public.application_user.user_id;


--
-- Name: authorization_token; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.authorization_token (
    authorization_id integer NOT NULL,
    user_id integer,
    origin public.token_origin,
    refresh_token character varying(255),
    invalid_token boolean DEFAULT false,
    refresh_lock timestamp with time zone,
    last_refreshed_at timestamp without time zone
);


--
-- Name: authorization_token_authorization_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.authorization_token_authorization_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: authorization_token_authorization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.authorization_token_authorization_id_seq OWNED BY public.authorization_token.authorization_id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: application_user user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user ALTER COLUMN user_id SET DEFAULT nextval('public.application_user_user_id_seq'::regclass);


--
-- Name: authorization_token authorization_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token ALTER COLUMN authorization_id SET DEFAULT nextval('public.authorization_token_authorization_id_seq'::regclass);


--
-- Name: application_user application_user_external_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user
    ADD CONSTRAINT application_user_external_user_id_key UNIQUE (external_user_id);


--
-- Name: application_user application_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.application_user
    ADD CONSTRAINT application_user_pkey PRIMARY KEY (user_id);


--
-- Name: authorization_token authorization_token_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token
    ADD CONSTRAINT authorization_token_pkey PRIMARY KEY (authorization_id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: authorization_token authorization_token_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.authorization_token
    ADD CONSTRAINT authorization_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.application_user(user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20240211001319');
