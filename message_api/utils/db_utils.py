import sqlite3

from message_api import config


def _get_db_connection():
    """Establishes a connection to the SQLite database."""
    connection_obj = sqlite3.connect(config.DATABASE_PATH)
    connection_obj.row_factory = sqlite3.Row
    return connection_obj


def initialize_database():
    """Creates the chat_history table if it doesn't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS chat_history
                   (
                       id        INTEGER PRIMARY KEY AUTOINCREMENT,
                       role      TEXT NOT NULL,
                       content   TEXT NOT NULL,
                       timestamp TEXT NOT NULL
                   )
                   """)
    conn.commit()
    conn.close()


def add_message_to_db(role: str, content: str, timestamp: str):
    """Adds a new chat message to the database."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, timestamp)
    )
    conn.commit()
    conn.close()


def load_history_from_db():
    """Loads all messages from the chat_history table, ordered by time."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM chat_history ORDER BY timestamp ASC")
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history
