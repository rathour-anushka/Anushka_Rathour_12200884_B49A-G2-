from fastapi import APIRouter, Depends, HTTPException, Form
import sqlite3
from ..database import get_connection

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============ USER MANAGEMENT ============

@router.get("/users")
async def get_users(conn: sqlite3.Connection = Depends(get_connection)):
    """Get all users from the database."""
    try:
        cursor = conn.execute("SELECT id, student_id, role FROM users ORDER BY student_id")
        users = [
            {"id": row[0], "student_id": row[1], "role": row[2]}
            for row in cursor.fetchall()
        ]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")


@router.post("/add-user")
async def add_user(
    student_id: str = Form(...),
    passcode: str = Form(...),
    role: str = Form(...),
    conn: sqlite3.Connection = Depends(get_connection),
):
    """Add a new user."""
    if role not in ["student", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    try:
        conn.execute(
            "INSERT INTO users (student_id, passcode, role) VALUES (?, ?, ?)",
            (student_id, passcode, role),
        )
        conn.commit()
        return {"message": "User added successfully", "student_id": student_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Student ID already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user: {str(e)}")


@router.delete("/delete-user/{user_id}")
async def delete_user(
    user_id: int,
    conn: sqlite3.Connection = Depends(get_connection),
):
    """Delete a user by ID."""
    try:
        cursor = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")


@router.post("/update-user/{user_id}")
async def update_user(
    user_id: int,
    student_id: str = Form(None),
    passcode: str = Form(None),
    role: str = Form(None),
    conn: sqlite3.Connection = Depends(get_connection),
):
    """Update user information."""
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        student_id = student_id or user[1]
        passcode = passcode or user[2]
        role = role or user[3]

        if role not in ["student", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role")

        conn.execute(
            "UPDATE users SET student_id = ?, passcode = ?, role = ? WHERE id = ?",
            (student_id, passcode, role, user_id),
        )
        conn.commit()
        return {"message": "User updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


# ============ ITEM MANAGEMENT ============

@router.post("/update-item-status/{item_id}")
async def update_item_status(
    item_id: int,
    status: str = Form(...),
    conn: sqlite3.Connection = Depends(get_connection),
):
    """Update the status of an item."""
    valid_statuses = ["Yet to be found", "Lost", "Found", "Resolved"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        cursor = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Item not found")

        conn.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
        conn.commit()
        return {"message": f"Item status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating status: {str(e)}")


@router.get("/item-stats")
async def get_item_stats(conn: sqlite3.Connection = Depends(get_connection)):
    """Get statistics about items and users."""
    try:
        items_total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        items_lost = conn.execute(
            "SELECT COUNT(*) FROM items WHERE status = 'Lost'"
        ).fetchone()[0]
        items_found = conn.execute(
            "SELECT COUNT(*) FROM items WHERE status = 'Found'"
        ).fetchone()[0]
        items_resolved = conn.execute(
            "SELECT COUNT(*) FROM items WHERE status = 'Resolved'"
        ).fetchone()[0]

        users_total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        admins_total = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin'"
        ).fetchone()[0]

        return {
            "items": {
                "total": items_total,
                "lost": items_lost,
                "found": items_found,
                "resolved": items_resolved,
            },
            "users": {"total": users_total, "admins": admins_total},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")
