-- First we create the schema.
CREATE SCHEMA IF NOT EXISTS "echoes"
    AUTHORIZATION "postgres";

SET search_path TO "echoes";

DO $$ BEGIN
    CREATE TYPE PRIVACY_ENUM AS ENUM ('public', 'private');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE IF NOT EXISTS "playlist" (
    id SERIAL,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    owner_id BIGINT NOT NULL,
    description VARCHAR(255) DEFAULT 'No description provided',
    times_played INT NOT NULL DEFAULT 0,
    privacy PRIVACY_ENUM DEFAULT 'public',
    icon_url TEXT DEFAULT 'https://avatars.githubusercontent.com/u/70459826?v=4',
    created_at TIMESTAMP WITHOUT TIME ZONE
    DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT pk PRIMARY KEY (id),
    CONSTRAINT uni_pk UNIQUE (id),
    CONSTRAINT name_pk UNIQUE (name)
);