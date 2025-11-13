import json
import sqlite3

from message_api import config


def _get_db_connection():
    """Establishes a connection to the SQLite database."""
    connection_obj = sqlite3.connect(config.DATABASE_PATH)
    connection_obj.row_factory = sqlite3.Row
    return connection_obj


def initialize_database():
    """Creates all necessary tables if they don't exist."""
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

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS raw_messages
                   (
                       id        TEXT PRIMARY KEY,
                       json_body TEXT NOT NULL
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS identities
                   (
                       id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                       name                TEXT NOT NULL,
                       external_message_id TEXT NOT NULL,
                       FOREIGN KEY (external_message_id) REFERENCES raw_messages (id)
                   )
                   """)

    cursor.execute("""
                   CREATE UNIQUE INDEX IF NOT EXISTS idx_name_message_id ON identities (name, external_message_id)
                   """)

    conn.commit()
    conn.close()


def add_message_to_chat_history(role: str, content: str, timestamp: str):
    """Adds a new chat message to the chat_history table."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, timestamp)
    )
    conn.commit()
    conn.close()


def load_chat_history():
    """Loads all messages from the chat_history table, ordered by time."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM chat_history ORDER BY timestamp ASC")
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


def get_raw_message_count():
    """Returns the total number of messages stored in the raw_messages table."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM raw_messages")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def add_raw_message(message_id: str, message_data: dict):
    """
    Adds a raw message to the database, ignoring it if the ID already exists.
    Returns True if a new row was inserted, False otherwise.
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO raw_messages (id, json_body) VALUES (?, ?)",
        (message_id, json.dumps(message_data))
    )
    was_inserted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return was_inserted


def add_identity_record(name: str, external_message_id: str):
    """Adds an identity record to the database, ignoring duplicates."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO identities (name, external_message_id) VALUES (?, ?)",
        (name, external_message_id)
    )
    conn.commit()
    conn.close()
