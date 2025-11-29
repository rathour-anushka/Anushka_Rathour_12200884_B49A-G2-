import io
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer


# Using larger, more accurate CLIP model for better image matching across different angles
model = SentenceTransformer("clip-ViT-L-14")


def get_embedding(text=None, image_data=None, title=None):
    """Return a CLIP embedding for text, image, or both.
    
    Args:
        text: Description text
        image_data: Image bytes
        title: Item title (will be prepended to text if provided)
    """
    # Combine title and text for better text matching-
    if title and text:
        text = f"{title}. {text}"
    elif title and not text:
        text = title
    
    if text is None and image_data is None:
        raise ValueError("Provide text or image")

    embeddings = []

    if text:
        embeddings.append(
            model.encode(text, convert_to_tensor=True, normalize_embeddings=True)
        )

    if image_data:
        image = Image.open(image_data).convert("RGB")
        embeddings.append(
            model.encode(image, convert_to_tensor=True, normalize_embeddings=True)
        )

    return (
        torch.mean(torch.stack(embeddings), dim=0)
        if len(embeddings) == 2
        else embeddings[0]
    )

