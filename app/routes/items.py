from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from ..database import get_connection
from ..utils.embeddings import get_embedding
from ..utils.image_utils import save_image
import json
from pathlib import Path

router = APIRouter()


@router.post("/add-item")
async def add_item(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    phone: str = Form(...),
    image: UploadFile = File(None),
):
    """Create a new lost/found item and store its embedding."""
    if not title or not description or not category or not location or not phone:
        raise HTTPException(status_code=400, detail="All fields are required")

    image_path, image_data = (None, None)
    if image:
        image_path, image_data = save_image(image)

    # Generate embedding with title + description for better text matching
    embedding = get_embedding(text=description, image_data=image_data, title=title)

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO items (title, description, category, location, phone, image_path, embedding) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                title,
                description,
                category,
                location,
                phone,
                image_path,
                json.dumps(embedding.cpu().tolist()),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {"message": "Item added successfully", "title": title}

@router.get("/items")
async def list_items():
    """Return all items ordered by newest first."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, title, description, category, location, phone, image_path FROM items ORDER BY id DESC"
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    # Normalize image paths so frontend can use them directly.
    result = []
    for r in rows:
        image_path = r[6]
        if image_path:
            # Ensure stored filename becomes a URL under /uploads
            if str(image_path).startswith("/uploads/"):
                image_url = image_path
            else:
                image_url = f"/uploads/{image_path}"
        else:
            image_url = None

        result.append(
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "category": r[3],
                "location": r[4],
                "phone": r[5],
                "image_path": image_url,
            }
        )

    return result

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item and its image file if present."""
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT image_path FROM items WHERE id = ?", (item_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")

        image_path = row[0]
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()

    if image_path:
        Path(image_path).unlink(missing_ok=True)

    return {"message": "Item deleted", "id": item_id}

@router.post("/update-item/{item_id}")
async def update_item(
    item_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    phone: str = Form(...),
    image: UploadFile = File(None),
):
    try:
        image_path, image_data = (None, None)
        if image:
            image_path, image_data = save_image(image)

        embedding = get_embedding(text=description, image_data=image_data)
        conn = get_connection()

        if image_path:
            conn.execute(
                "UPDATE items SET title=?, description=?, category=?, location=?, phone=?, image_path=?, embedding=? WHERE id=?",
                (title, description, category, location, phone, image_path, json.dumps(embedding.cpu().tolist()), item_id),
            )
        else:
            conn.execute(
                "UPDATE items SET title=?, description=?, category=?, location=?, phone=?, embedding=? WHERE id=?",
                (title, description, category, location, phone, json.dumps(embedding.cpu().tolist()), item_id),
            )

        conn.commit()
        return {"message": "Item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@router.post("/mark-resolved/{item_id}")
async def mark_resolved(item_id: int):
    try:
        conn = get_connection()
        conn.execute("UPDATE items SET status = 'Resolved' WHERE id = ?", (item_id,))
        conn.commit()
        return {"message": "Item marked as resolved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")
