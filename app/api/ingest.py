import io
from typing import Annotated, Literal
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.models.db_models import Document
from app.schemas.schemas import IngestResponse
from app.services.chunker import chunk_text
from app.services.embedder import embed_texts
from app.services.vector_store import store_embeddings

import pypdf

router = APIRouter(prefix="/ingest", tags=["Ingestion"])
settings = get_settings()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file."""
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(texts)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode plain text file."""
    return file_bytes.decode("utf-8", errors="ignore")


@router.post("/", response_model=IngestResponse)
async def ingest_document(
    file: Annotated[UploadFile, File(description="Upload a .pdf or .txt file")],
    chunk_strategy: Annotated[
        Literal["fixed", "semantic"],
        Form(description="Chunking strategy: 'fixed' or 'semantic'"),
    ] = "fixed",
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    """
    Upload a document, extract text, chunk it, embed chunks, and store in Qdrant.
    Document metadata is saved to PostgreSQL.
    """
    filename = file.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower()

    if file_ext not in ("pdf", "txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf and .txt files are supported.",
        )

    file_bytes = await file.read()

    # Extract text based on file type
    if file_ext == "pdf":
        text = extract_text_from_pdf(file_bytes)
    else:
        text = extract_text_from_txt(file_bytes)

    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from file.")

    # Chunk the text
    chunks = chunk_text(text, strategy=chunk_strategy)
    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks generated from document.")

    # Generate embeddings
    embeddings = embed_texts(chunks)

    # Store in Qdrant
    collection_name = settings.qdrant_collection_name
    store_embeddings(
        collection_name=collection_name,
        chunks=chunks,
        embeddings=embeddings,
        metadata={"filename": filename, "chunk_strategy": chunk_strategy},
    )

    # Save metadata to PostgreSQL
    doc = Document(
        filename=filename,
        file_type=file_ext,
        chunk_strategy=chunk_strategy,
        num_chunks=len(chunks),
        collection_name=collection_name,
    )
    db.add(doc)
    await db.commit()

    return IngestResponse(
        message="Document ingested successfully.",
        filename=filename,
        chunk_strategy=chunk_strategy,
        num_chunks=len(chunks),
        collection_name=collection_name,
    )