-- migrate:up

CREATE TABLE application_user (
    id SERIAL PRIMARY KEY,
    external_user_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);


CREATE TYPE token_origin AS ENUM ('twitch', 'spotify');


CREATE TABLE authorization_token (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES application_user(id) ON DELETE CASCADE,
    origin token_origin, -- Specify the data type for the 'origin' column
    access_tokn VARCHAR(255),
    refresh_token VARCHAR(255) not null,
    invalid_token BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMPTZ,
);


-- migrate:down

DROP TABLE authorization_token;
DROP TABLE user;
DROP TYPE token_origin;

