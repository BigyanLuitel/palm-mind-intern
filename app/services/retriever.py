from app.services.embedder import embed_query
from app.services.vector_store import search_similar
from app.services.memory import get_history, append_message
from app.services.llm import chat_completion
from app.core.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a helpful AI assistant. Answer questions based on the provided document context.
If the context does not contain enough information, say so honestly.
Do not make up facts.

If the user wants to book an interview, collect their:
- Full name
- Email address
- Preferred date
- Preferred time

Once you have all four details, confirm the booking clearly."""


def build_prompt(
    context: str,
    history: list[dict],
    user_message: str,
) -> list[dict]:
    """
    Manually construct the full message list for the LLM:
    system prompt + chat history + retrieved context + user query.
    """
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject retrieved context as a system-level context block
    if context:
        messages.append({
            "role": "system",
            "content": f"Relevant document context:\n\n{context}",
        })

    # Append conversation history
    messages.extend(history)

    # Append current user message
    messages.append({"role": "user", "content": user_message})

    return messages


def retrieve_context(query: str, collection_name: str) -> str:
    """
    Embed the query, search Qdrant, and return concatenated chunk texts.
    """
    query_vector = embed_query(query)
    results = search_similar(
        collection_name=collection_name,
        query_vector=query_vector,
        top_k=settings.retrieval_top_k,
    )
    chunks = [hit.payload.get("text", "") for hit in results if hit.payload]
    return "\n\n---\n\n".join(chunks)


def run_rag(
    session_id: str,
    user_message: str,
    collection_name: str,
) -> str:
    """
    Full custom RAG pipeline:
    1. Retrieve relevant chunks from Qdrant
    2. Load chat history from Redis
    3. Build prompt manually
    4. Call Groq LLM
    5. Save exchange to Redis
    6. Return assistant response
    """
    # Step 1 — retrieve context
    context = retrieve_context(user_message, collection_name)

    # Step 2 — load history
    history = get_history(session_id, limit=settings.chat_history_length)

    # Step 3 — build prompt
    messages = build_prompt(context, history, user_message)

    # Step 4 — call LLM
    response = chat_completion(messages)

    # Step 5 — persist to Redis
    append_message(session_id, "user", user_message)
    append_message(session_id, "assistant", response)

    return response