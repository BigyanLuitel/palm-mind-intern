import json
from app.services.llm import chat_completion

BOOKING_KEYWORDS = {"book", "schedule", "interview", "appointment", "meeting", "slot"}

EXTRACTION_PROMPT = """You are an information extractor. 
From the conversation below, extract interview booking details if all four are present.

Return ONLY a valid JSON object with these exact keys:
{{
  "name": "full name or null",
  "email": "email address or null",
  "date": "date string or null",
  "time": "time string or null"
}}

If any field is missing, set it to null.
Do not include any explanation or extra text — only the JSON object.

Conversation:
{conversation}
"""


def is_booking_intent(message: str) -> bool:
    """Quick keyword check to detect potential booking intent."""
    lower = message.lower()
    return any(keyword in lower for keyword in BOOKING_KEYWORDS)


def extract_booking_details(
    conversation_history: list[dict],
    latest_message: str,
) -> dict | None:
    """
    Use the LLM to extract structured booking info from the conversation.
    Returns a dict with name/email/date/time if all present, else None.
    """
    # Format conversation for extraction
    formatted = ""
    for msg in conversation_history:
        role = msg.get("role", "user").capitalize()
        content = msg.get("content", "")
        formatted += f"{role}: {content}\n"
    formatted += f"User: {latest_message}"

    prompt = EXTRACTION_PROMPT.format(conversation=formatted)

    raw = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=256,
    )

    try:
        clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(clean)

        # Only return if all four fields are present and non-null
        if all(data.get(k) for k in ("name", "email", "date", "time")):
            return data
    except (json.JSONDecodeError, AttributeError):
        pass

    return None