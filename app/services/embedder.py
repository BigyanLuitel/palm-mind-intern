from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and cache it."""
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text chunks."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query string."""
    model = get_embedding_model()
    embedding = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    return embedding[0].tolist()