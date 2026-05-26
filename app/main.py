from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import init_db
from app.api import ingest, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Palm Mind RAG API",
    description="Document ingestion and conversational RAG backend with interview booking support.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ingest.router)
app.include_router(chat.router)


@app.get("/", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok", "message": "Palm Mind RAG API is running."}