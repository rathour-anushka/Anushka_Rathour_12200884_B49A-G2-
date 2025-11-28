import io
import time
from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..config import UPLOAD_DIR, ALLOWED_EXTENSIONS


def save_image(image: UploadFile) -> tuple[str, io.BytesIO]:
    """Persist an uploaded image and return its path and bytes buffer."""
    if not image or not image.filename:
        raise HTTPException(status_code=400, detail="No image file provided")

    ext = Path(image.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{int(time.time())}_{Path(image.filename).name}"
    save_path = Path(UPLOAD_DIR) / filename
    save_path.parent.mkdir(parents=True, exist_ok=True)

    content = image.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    with open(save_path, "wb") as f:
        f.write(content)

    with open(save_path, "rb") as img_file:
        image_data = io.BytesIO(img_file.read())

    return str(save_path).replace("\\", "/"), image_data

