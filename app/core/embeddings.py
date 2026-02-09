
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_text(text: str) -> np.ndarray:
    """Generate real semantic embeddings"""
    if not text.strip():
        # Return zero vector for empty text
        return np.zeros(384)

    # Generate embedding
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding