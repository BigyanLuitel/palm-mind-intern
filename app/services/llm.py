from groq import Groq
from app.core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_groq_client() -> Groq:
    """Initialize and cache the Groq client."""
    return Groq(api_key=settings.groq_api_key)


def chat_completion(
    messages: list[dict],
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Call Groq chat completions API.
    messages: list of {"role": "user"|"assistant"|"system", "content": str}
    Returns the assistant response as a string.
    """
    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()