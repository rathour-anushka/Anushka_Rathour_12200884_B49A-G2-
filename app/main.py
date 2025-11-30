from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .routes import auth, items, search, admin
from .utils.auth import authenticate_user
from .config import UPLOAD_DIR
from .database import init_db, get_connection

# Base directory for resolving paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent  # Go up one level to project root

# Initialize FastAPI app
app = FastAPI(title="Campus Lost & Found AI")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static and upload directories
app.mount("/uploads", StaticFiles(directory=PROJECT_ROOT / UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

"""Main FastAPI application setup."""

# Set up Jinja2 templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Dependency to get DB connection
def get_db():
    """Dependency to get a database connection and close it after the request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# Initialize database and tables at startup
init_db()

# Include modular routers
app.include_router(items.router, tags=["Items"])
app.include_router(search.router, tags=["Search"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(admin.router, tags=["Admin"])

# Serve login page at root
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Handle login and redirect based on role
@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    student_id: str = Form(...),
    passcode: str = Form(...),
    conn: sqlite3.Connection = Depends(get_db),
):
    role = authenticate_user(student_id, passcode)
    if not role:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
        )
    if role == "admin":
        return RedirectResponse(url="/admin-dashboard", status_code=303)
    # Student view: load items for index.html
    items = conn.execute(
        "SELECT id, title, description, category, location, phone, image_path FROM items ORDER BY id DESC"
    ).fetchall()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "student_id": student_id, "items": items},
    )

# Student report page (optional direct access)
@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    items = conn.execute(
        "SELECT id, title, description, category, location, phone, image_path FROM items ORDER BY id DESC"
    ).fetchall()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "student_id": "student", "items": items},
    )

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("admin_token")  # if using cookies
    return response
@app.get("/change-password", response_class=HTMLResponse)
async def change_password_form(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})
@app.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    student_id: str = Form(...),
    old_passcode: str = Form(...),
    new_passcode: str = Form(...),
    conn: sqlite3.Connection = Depends(get_db),
):
    user = conn.execute(
        "SELECT passcode FROM users WHERE student_id = ?", (student_id,)
    ).fetchone()
    if not user or user[0] != old_passcode:
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "error": "Invalid credentials"},
        )
    conn.execute(
        "UPDATE users SET passcode = ? WHERE student_id = ?",
        (new_passcode, student_id),
    )
    conn.commit()
    return templates.TemplateResponse(
        "change_password.html",
        {
            "request": request,
            "message": "Password updated successfully. Please log in again.",
        },
    )

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_form(request: Request):
    """Display forgot password form."""
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password(
    request: Request,
    student_id: str = Form(...),
    new_passcode: str = Form(...),
    confirm_passcode: str = Form(...),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Reset password for user who forgot it."""
    # Check if passcodes match
    if new_passcode != confirm_passcode:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "error": "Passcodes do not match"},
        )
    
    # Check if student ID exists
    user = conn.execute(
        "SELECT id FROM users WHERE student_id = ?", (student_id,)
    ).fetchone()
    if not user:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "error": "Student ID not found in system"},
        )
    
    # Check passcode length
    if len(new_passcode) < 3:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "error": "Passcode must be at least 3 characters"},
        )
    
    # Update passcode
    try:
        conn.execute(
            "UPDATE users SET passcode = ? WHERE student_id = ?",
            (new_passcode, student_id),
        )
        conn.commit()
        return templates.TemplateResponse(
            "forgot_password.html",
            {
                "request": request,
                "success": "Passcode reset successfully! Please log in with your new passcode.",
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "error": f"An error occurred: {str(e)}"},
        )

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    items = conn.execute("SELECT id, title, description, category, location, phone, image_path, status FROM items ORDER BY id DESC").fetchall()
    items = []
    for item in conn.execute("SELECT id, title, description, category, location, phone, image_path, status FROM items ORDER BY id DESC").fetchall():
        item_dict = dict(item)
        if item_dict["image_path"]:
            item_dict["image_path"] = f"/uploads/{item_dict['image_path']}"
        items.append(item_dict)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "items": items})
