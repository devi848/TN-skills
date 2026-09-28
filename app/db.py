import json
import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone

from .config import DATABASE_PATH


def now():
    return datetime.now(
        timezone.utc
    ).isoformat()


@contextmanager
def db():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys=ON"
    )

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def init_db():
    with db() as connection:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner_type TEXT NOT NULL,
                title TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                image_path TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY(user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS
            idx_rec_user
            ON recommendations(
                user_id,
                created_at DESC
            );
            """
        )


def user_username(username):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()


def user_email(email):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),)
        ).fetchone()


def user_id(user_id_value):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id_value,)
        ).fetchone()


def create_user(
    username,
    email,
    full_name,
    password_hash
):
    with db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (
                username,
                email,
                full_name,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username.strip(),
                email.strip().lower(),
                full_name.strip() or None,
                password_hash,
                now()
            )
        )

        return cursor.lastrowid


def save_rec(
    user_id_value,
    planner_type,
    title,
    input_data,
    result_data,
    image_path=None
):
    with db() as connection:
        cursor = connection.execute(
            """
            INSERT INTO recommendations (
                user_id,
                planner_type,
                title,
                input_json,
                result_json,
                image_path,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id_value,
                planner_type,
                title,
                json.dumps(
                    input_data,
                    ensure_ascii=False
                ),
                json.dumps(
                    result_data,
                    ensure_ascii=False
                ),
                image_path,
                now()
            )
        )

        return cursor.lastrowid


def recs(user_id_value, limit=50):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM recommendations
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                user_id_value,
                limit
            )
        ).fetchall()


def rec(user_id_value, recommendation_id):
    with db() as connection:
        return connection.execute(
            """
            SELECT *
            FROM recommendations
            WHERE id = ?
            AND user_id = ?
            """,
            (
                recommendation_id,
                user_id_value
            )
        ).fetchone()