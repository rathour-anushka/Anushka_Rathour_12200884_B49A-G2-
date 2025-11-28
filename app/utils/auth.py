import sqlite3
from ..config import DB_PATH


def authenticate_user(student_id: str, passcode: str):
    """Return the user's role if credentials are valid, otherwise None."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(
            "SELECT role FROM users WHERE student_id = ? AND passcode = ?",
            (student_id, passcode),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

