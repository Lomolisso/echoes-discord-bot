from os.path import isfile
from typing import Union
from winsound import PlaySound
from psycopg2 import connect
from psycopg2 import errors
from apscheduler.triggers.cron import CronTrigger
from tzlocal import get_localzone_name

""" PostgreSQL parameters needed in order to connect to db """
DB_NAME = "echoes"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

""" Database related paths """
DB_PATH = "./data/db/database.db"
BUILD_PATH = "./data/db/build.sql"

conn = connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()

def commit():
    conn.commit()
    print("[*] Commiting...")

def autosave(scheduler):
    scheduler.add_job(func=commit, trigger=CronTrigger(timezone=get_localzone_name(), second=0))

def close():
    conn.close()

def with_commit(fun):
    def inner(*args, **kwargs):
        ret = fun(*args, **kwargs)
        commit()
        return ret
    return inner

@with_commit
def build():
    if isfile(BUILD_PATH):
        executescript(BUILD_PATH)


def execute(command, *values):
    cursor.execute(command, tuple(values))

def executemany(command, valueset):
    cursor.executemany(command, valueset)

def executescript(path):
    with open(path, 'r', encoding="utf-8") as script:
        cursor.execute(script.read())

def fetchall(command, *values):
    execute(command, tuple(values))
    return cursor.fetchall()

def fetchmany(n, command, *values):
    execute(command, tuple(values))
    return cursor.fetchmany(n)

def fetchone(command, *values):
    execute(command, tuple(values))
    return cursor.fetchone()

class Playlist:
    """
    TODO: Docs static class.
    """
    FIELDS = [
        "name",
        "url",
        "owner_name",
        "owner_id",
        "description",
        "times_played",
        "privacy",
        "icon_url",
        "created_at",
    ]

    EDITABLE_FIELDS = [
        "name",
        "url",
        "description",
        "privacy",
        "icon_url",
    ]

    RANKING_LIMIT = 10

    @staticmethod
    @with_commit
    def create(name, url, owner_name, owner_id) -> tuple[bool, str]:
        """Saves a playlist in the database."""
        values = (name, url, owner_name, owner_id)
        command = """
        INSERT INTO playlist (name, url, owner_name, owner_id)
        VALUES(%s, %s, %s, %s)
        """

        try:
            execute(command, *values)
        except errors.UniqueViolation as e:
            print("[*] DB error: save_playlist (UniqueViolation)")
            return (False, "The playlist name was already taken.")

        return (True, "ok")

    @staticmethod
    def get_by_name(name: str) -> dict:
        """Gets by name (primary key) a playlist from the database."""
        command = f"""
        SELECT *
        FROM playlist
        WHERE name = '{name}'
        """
        playlist_tuple = fetchone(command, ())
        if playlist_tuple is None:
            return None
        return dict(zip(Playlist.FIELDS, playlist_tuple))
    

    @staticmethod
    def set_property(playlist_name: str, property_name: str, value: str) -> tuple[bool, str]:
        if property_name not in Playlist.FIELDS:
            return (False, f"The property `{property_name}` does not exists.")
        
        if property_name not in Playlist.EDITABLE_FIELDS:
            return (False, f"The property `{property_name}` cannot be modified.")
        
        if property_name == 'name' and Playlist.get_by_name(value) is not None:
            return (False, f"The playlist `{value}` already exists.")
        
        command = f"""
        UPDATE playlist
        SET {property_name} = '{value}'
        WHERE name = '{playlist_name}'
        """
        execute(command, ())
        return (True, "ok")

    @staticmethod
    def get_ranking() -> list[dict]:
        command = f"""
        SELECT *
        FROM playlist
        ORDER BY times_played ASC,
        name DESC
        """
        ranking_tuples = fetchmany(Playlist.RANKING_LIMIT, command, ())
        return [dict(zip(Playlist.FIELDS, playlist_tuple)) for playlist_tuple in ranking_tuples]
            