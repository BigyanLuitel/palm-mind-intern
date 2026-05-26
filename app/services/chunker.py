from typing import Literal
from app.core.config import get_settings

settings = get_settings()


def fixed_chunker(text: str) -> list[str]:
    """
    Strategy 1: Fixed-size chunking with overlap.
    Splits text into chunks of fixed character size with a sliding overlap window.
    """
    chunk_size = settings.fixed_chunk_size
    overlap = settings.fixed_chunk_overlap
    chunks: list[str] = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def semantic_chunker(text: str) -> list[str]:
    """
    Strategy 2: Semantic chunking based on sentence boundaries.
    Splits on paragraph and sentence boundaries, then groups sentences
    into chunks that stay within the token budget.
    """
    token_budget = settings.fixed_chunk_size
    chunks: list[str] = []

    # Split into paragraphs first
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    sentences: list[str] = []
    for para in paragraphs:
        raw = para.replace("\n", " ")
        parts = raw.split(". ")
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if i < len(parts) - 1 and not part.endswith((".", "!", "?")):
                part += "."
            sentences.append(part)

    # Group sentences into chunks within token budget
    current_chunk: list[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)
        if current_length + sentence_length > token_budget and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def chunk_text(
    text: str,
    strategy: Literal["fixed", "semantic"] = "fixed",
) -> list[str]:
    """Entry point — selects chunking strategy and returns list of chunks."""
    if strategy == "semantic":
        return semantic_chunker(text)
    return fixed_chunker(text)