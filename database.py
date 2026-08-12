import sqlite3

DATABASE = "users.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            two_factor_enabled INTEGER NOT NULL DEFAULT 0,
            two_factor_secret TEXT
        )
    """)

    connection.commit()

    # Add 2FA columns if the database already existed
    columns = connection.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "two_factor_enabled" not in column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN two_factor_enabled INTEGER NOT NULL DEFAULT 0"
        )

    if "two_factor_secret" not in column_names:
        connection.execute(
            "ALTER TABLE users ADD COLUMN two_factor_secret TEXT"
        )

    connection.commit()
    connection.close()


def create_user(username, password_hash):
    connection = get_connection()

    try:
        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_user(username):
    connection = get_connection()

    user = connection.execute(
    """
    SELECT id, username, password_hash,
           two_factor_enabled, two_factor_secret
    FROM users
    WHERE username = ?
    """,
    (username,)
).fetchone()


    connection.close()

    return user