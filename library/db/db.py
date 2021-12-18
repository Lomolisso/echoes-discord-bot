from os.path import isfile
from typing import ValuesView
from psycopg2 import connect

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

def execture(command, *values):
    cursor.execute(command, tuple(values))

def executemany(command, valueset):
    cursor.executemany(command, valueset)

def executescript(path):
    with open(path, 'r', encoding="utf-8") as script:
        cursor.execute(script.read())






