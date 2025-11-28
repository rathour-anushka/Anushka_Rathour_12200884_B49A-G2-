import sqlite3
from .config import DB_PATH


def get_connection():
    """Return a SQLite connection with basic settings."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create schema and seed default users if needed."""
    conn = get_connection()

    # Create items table with phone instead of email
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            phone TEXT NOT NULL,
            image_path TEXT,
            embedding TEXT,
            status TEXT DEFAULT 'Yet to be found'
        )
        """
    )

    # Create users table
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            passcode TEXT NOT NULL,
            role TEXT CHECK(role IN ('student', 'admin')) NOT NULL
        )
        """
    )

    # Insert default users
    conn.execute(
        "INSERT OR IGNORE INTO users (student_id, passcode, role) VALUES (?, ?, ?)",
        ("admin01", "adminpass", "admin"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (student_id, passcode, role) VALUES (?, ?, ?)",
        ("S12345", "pass123", "student"),
    )

    conn.commit()
    conn.close()

