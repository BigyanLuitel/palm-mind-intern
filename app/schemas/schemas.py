from pydantic import BaseModel
from datetime import datetime
from typing import Literal


# ── Ingest ────────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    message: str
    filename: str
    chunk_strategy: Literal["fixed", "semantic"]
    num_chunks: int
    collection_name: str


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str


class BookingInfo(BaseModel):
    name: str
    email: str
    date: str
    time: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    booking_detected: bool = False
    booking_info: BookingInfo | None = None


# ── Document metadata ─────────────────────────────────────────────────────────

class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    chunk_strategy: str
    num_chunks: int
    collection_name: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ── Booking metadata ──────────────────────────────────────────────────────────

class BookingOut(BaseModel):
    id: int
    session_id: str
    name: str
    email: str
    date: str
    time: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True