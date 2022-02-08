from os.path import isfile
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

@with_commit
def save_playlist(ctx, name, url) -> tuple[bool, str]:
    values = (name, url, ctx.author.display_name, ctx.author.id)
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

def get_playlist_by_name(name: str) -> tuple:
    command = f"""
    SELECT *
    FROM playlist
    WHERE name = '{name}'
    """
    return fetchone(command, ())

