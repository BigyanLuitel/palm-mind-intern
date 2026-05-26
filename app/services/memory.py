import json
import redis
from app.core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_redis_client() -> redis.Redis:
    """Initialize and cache the Redis client."""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
        ssl=False,
    )


def _session_key(session_id: str) -> str:
    return f"chat_history:{session_id}"


def append_message(session_id: str, role: str, content: str) -> None:
    """Append a single message to the session chat history in Redis."""
    client = get_redis_client()
    message = json.dumps({"role": role, "content": content})
    client.rpush(_session_key(session_id), message)


def get_history(session_id: str, limit: int | None = None) -> list[dict]:
    """
    Retrieve chat history for a session.
    Returns the last `limit` messages if specified.
    """
    client = get_redis_client()
    key = _session_key(session_id)
    limit = limit or settings.chat_history_length
    raw_messages = client.lrange(key, -limit, -1)
    return [json.loads(msg) for msg in raw_messages]


def clear_history(session_id: str) -> None:
    """Delete all chat history for a session."""
    client = get_redis_client()
    client.delete(_session_key(session_id))