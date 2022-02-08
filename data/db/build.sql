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
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    owner_id BIGINT NOT NULL,
    description VARCHAR(255) DEFAULT 'No description provided',
    times_played INT NOT NULL DEFAULT 0,
    privacy PRIVACY_ENUM DEFAULT 'public',
    icon_url TEXT DEFAULT 'https://i.imgur.com/jWkaANP.png',
    created_at TIMESTAMP WITHOUT TIME ZONE
    DEFAULT (NOW() AT TIME ZONE 'UTC'),
    CONSTRAINT pk PRIMARY KEY (name),
    CONSTRAINT uni_pk UNIQUE (name)
);