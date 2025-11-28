from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from ..utils.embeddings import get_embedding
from ..database import get_connection
import torch, json, io
from torch.nn.functional import cosine_similarity

router = APIRouter()


@router.post("/search")
async def search_items(description: str = Form(""), image: UploadFile | None = File(None)):
    """Search items by text and/or image using embedding similarity.

    - Text-only searches: send `description` (may be empty string by default).
    - Image-only searches: send only `image`.
    """
    has_text = bool(description and description.strip())
    has_image = bool(image and image.filename)

    if not has_text and not has_image:
        raise HTTPException(
            status_code=400,
            detail="Please provide text description or upload an image to search",
        )

    # Build query embedding
    image_data = None
    if has_image:
        content = await image.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image file")
        image_data = io.BytesIO(content)

    try:
        query_emb = get_embedding(
            text=description if has_text else None, image_data=image_data
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Fetch items and compare embeddings
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, title, description, category, location, phone, image_path, embedding FROM items"
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    if not rows:
        return {"results": [], "message": "No items available to search"}

    results = []
    for r in rows:
        if not r[7]:
            continue

        emb = torch.tensor(json.loads(r[7]))
        similarity = cosine_similarity(
            query_emb.unsqueeze(0), emb.unsqueeze(0)
        ).item()
        results.append(
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "category": r[3],
                "location": r[4],
                "phone": r[5],
                "image_path": r[6],
                "similarity": round(similarity, 3),
            }
        )

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    
    # Lower threshold to 0.45 for better image matching across different angles
    # The L-14 model is more accurate, so this still filters out clearly unrelated items
    filtered_results = [r for r in results if r["similarity"] > 0.45]
    
    # Return top 10 results to avoid overwhelming users
    top_results = filtered_results[:10]

    return {
        "results": top_results,
        "total": len(top_results),
        "message": "Search completed successfully" if top_results else "No matching items found",
    }
