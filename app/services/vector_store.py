import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint,
)
from app.core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_qdrant_client() -> QdrantClient:
    """Initialize and cache the Qdrant client."""
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )


def ensure_collection(collection_name: str) -> None:
    """Create the Qdrant collection if it doesn't exist."""
    client = get_qdrant_client()
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dim,
                distance=Distance.COSINE,
            ),
        )


def store_embeddings(
    collection_name: str,
    chunks: list[str],
    embeddings: list[list[float]],
    metadata: dict,
) -> None:
    """
    Store text chunks and their embeddings in Qdrant.
    Each point carries the chunk text and document metadata as payload.
    """
    client = get_qdrant_client()
    ensure_collection(collection_name)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk,
                "filename": metadata.get("filename", ""),
                "chunk_index": idx,
                "chunk_strategy": metadata.get("chunk_strategy", ""),
            },
        )
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]

    client.upsert(collection_name=collection_name, points=points)


def search_similar(
    collection_name: str,
    query_vector: list[float],
    top_k: int = 5,
) -> list[ScoredPoint]:
    """Retrieve top-k most similar chunks from Qdrant."""
    client = get_qdrant_client()
    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )
    return results