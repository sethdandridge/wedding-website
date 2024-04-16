import contextlib
import sqlite3
from typing import Iterator

from flask import Flask, current_app


@contextlib.contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


@contextlib.contextmanager
def get_db_cursor() -> Iterator[sqlite3.Cursor]:
    with get_db() as db:
        cursor = db.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


def init_db(app: Flask) -> None:
    with app.app_context():
        with get_db() as db:
            with app.open_resource("db/schema.sql") as f:
                db.executescript(f.read().decode("utf8"))
            db.commit()
