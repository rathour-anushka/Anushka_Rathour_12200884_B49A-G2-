"""
Migration script to regenerate embeddings for existing items using the new CLIP model.

This script:
1. Loads all items from the database
2. Regenerates embeddings using the new clip-ViT-L-14 model with title + description
3. Updates the database with new embeddings

Run this after upgrading the CLIP model and before starting the server.
"""

import sqlite3
import json
import torch
from pathlib import Path
from PIL import Image
import io

# Import from app
from app.config import DB_PATH, UPLOAD_DIR
from app.utils.embeddings import get_embedding

def migrate_embeddings():
    """Regenerate all item embeddings with the new model."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all items
    cursor.execute("SELECT id, title, description, image_path FROM items")
    items = cursor.fetchall()
    
    print(f"Found {len(items)} items to migrate...")
    
    updated_count = 0
    error_count = 0
    
    for item_id, title, description, image_path in items:
        try:
            print(f"Processing item {item_id}: {title}...")
            
            # Load image if exists
            image_data = None
            if image_path:
                full_path = Path(image_path)
                if full_path.exists():
                    with open(full_path, "rb") as f:
                        image_data = io.BytesIO(f.read())
                else:
                    print(f"  Warning: Image not found at {image_path}")
            
            # Generate new embedding with title + description
            embedding = get_embedding(text=description, image_data=image_data, title=title)
            
            # Update database
            cursor.execute(
                "UPDATE items SET embedding = ? WHERE id = ?",
                (json.dumps(embedding.cpu().tolist()), item_id)
            )
            
            updated_count += 1
            print(f"  ✓ Updated embedding for item {item_id}")
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error processing item {item_id}: {str(e)}")
            continue
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print(f"Migration complete!")
    print(f"  Successfully updated: {updated_count} items")
    print(f"  Errors: {error_count} items")
    print("="*50)

if __name__ == "__main__":
    print("Starting embedding migration...")
    print("This will regenerate embeddings using clip-ViT-L-14 model")
    print("and include title in text embeddings.\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate_embeddings()
    else:
        print("Migration cancelled.")
