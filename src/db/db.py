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
        fun(*args, **kwargs)
        commit()
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

def save_playlist(**kwargs) -> tuple[bool, str]:
    try:
        ctx, playlist_name, playlist_url = kwargs["ctx"], kwargs["name"], kwargs["url"]
    except KeyError:
        print("[*] DB error: save_playlist (KeyError)")
        return (False, "An internal error has occurred.")
    
    values = (playlist_name, playlist_url, ctx.author.display_name, ctx.author.id)
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

