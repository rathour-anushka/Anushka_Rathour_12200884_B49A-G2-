import os

UPLOAD_DIR = "uploads"
DB_PATH = "database.db"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
