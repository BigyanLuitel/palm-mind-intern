from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.models.db_models import Booking
from app.schemas.schemas import ChatRequest, ChatResponse, BookingInfo
from app.services.retriever import run_rag
from app.services.memory import get_history, clear_history
from app.services.booking import is_booking_intent, extract_booking_details

router = APIRouter(prefix="/chat", tags=["Chat"])
settings = get_settings()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """
    Conversational RAG endpoint.
    - Retrieves relevant document chunks from Qdrant
    - Maintains multi-turn chat history via Redis
    - Detects interview booking intent and extracts structured info
    - Stores confirmed bookings in PostgreSQL
    """
    session_id = request.session_id
    user_message = request.message

    if not session_id.strip():
        raise HTTPException(status_code=400, detail="session_id cannot be empty.")
    if not user_message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Run custom RAG pipeline
    response = run_rag(
        session_id=session_id,
        user_message=user_message,
        collection_name=settings.qdrant_collection_name,
    )

    # Booking detection
    booking_detected = False
    booking_info: BookingInfo | None = None

    if is_booking_intent(user_message) or is_booking_intent(response):
        history = get_history(session_id)
        extracted = extract_booking_details(history, user_message)

        if extracted:
            booking_detected = True
            booking_info = BookingInfo(**extracted)

            # Persist booking to PostgreSQL
            booking = Booking(
                session_id=session_id,
                name=extracted["name"],
                email=extracted["email"],
                date=extracted["date"],
                time=extracted["time"],
            )
            db.add(booking)
            await db.commit()

    return ChatResponse(
        session_id=session_id,
        response=response,
        booking_detected=booking_detected,
        booking_info=booking_info,
    )


@router.delete("/{session_id}", summary="Clear chat history for a session")
async def clear_session(session_id: str) -> dict:
    """Delete all Redis chat history for a given session."""
    clear_history(session_id)
    return {"message": f"Chat history cleared for session '{session_id}'."}