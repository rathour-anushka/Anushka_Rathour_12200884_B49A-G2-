"""
Migration script to regenerate embeddings for existing items with the new CLIP-ViT-L-14 model.

Run this script after upgrading to the new model to update all existing items in the database.

Usage:
    python migrate_to_new_embeddings.py
"""

import sqlite3
import json
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.embeddings import get_embedding
from app.config import DB_PATH
import io


def migrate_embeddings():
    """Regenerate embeddings for all items using the new model and title+description."""
    
    print("🔄 Starting embedding migration...")
    print(f"📂 Database: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch all items
    cursor.execute("SELECT id, title, description, image_path FROM items")
    items = cursor.fetchall()
    
    if not items:
        print("✅ No items found in database. Nothing to migrate.")
        conn.close()
        return
    
    print(f"📊 Found {len(items)} items to migrate\n")
    
    success_count = 0
    error_count = 0
    
    for item_id, title, description, image_path in items:
        try:
            print(f"Processing item {item_id}: {title[:30]}...")
            
            # Load image if exists
            image_data = None
            if image_path and Path(image_path).exists():
                with open(image_path, "rb") as f:
                    image_data = io.BytesIO(f.read())
            
            # Generate new embedding with title + description
            embedding = get_embedding(text=description, image_data=image_data, title=title)
            
            # Update database
            cursor.execute(
                "UPDATE items SET embedding = ? WHERE id = ?",
                (json.dumps(embedding.cpu().tolist()), item_id)
            )
            
            success_count += 1
            print(f"  ✅ Updated successfully\n")
            
        except Exception as e:
            error_count += 1
            print(f"  ❌ Error: {str(e)}\n")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print(f"✅ Migration complete!")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {error_count}")
    print("="*50)
    
    if error_count > 0:
        print("\n⚠️  Some items failed to migrate. Check the errors above.")
    else:
        print("\n🎉 All items migrated successfully!")
        print("   You can now use the improved search with better image matching.")


if __name__ == "__main__":
    try:
        migrate_embeddings()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)
