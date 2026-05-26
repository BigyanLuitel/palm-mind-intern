# Palm Mind RAG API

A backend system built for document ingestion and conversational question answering with interview booking support.

Built with FastAPI, Qdrant, Redis, Supabase, and Groq (LLaMA 3.3 70B). No LangChain or RetrievalQAChain — the RAG pipeline is implemented from scratch.

## What it does

**Document Ingestion (`POST /ingest/`)** — Upload a PDF or TXT file. The system extracts text, chunks it using one of two strategies, generates embeddings, and stores them in Qdrant. File metadata is saved to PostgreSQL.

**Conversational RAG (`POST /chat/`)** — Ask questions over your uploaded documents. Chat history is stored in Redis per session, so follow-up questions work naturally. The system also detects when a user wants to book an interview, collects their details across multiple messages, and saves the booking to PostgreSQL.

## Tech stack

- FastAPI + Uvicorn
- Qdrant Cloud (vector storage)
- Redis Cloud (chat memory)
- Supabase / PostgreSQL (metadata + bookings)
- Groq — LLaMA 3.3 70B (LLM)
- HuggingFace sentence-transformers (embeddings, runs locally)
- SQLAlchemy async + psycopg

## Project structure

<pre>
app/
├── main.py
├── core/
│   ├── config.py        # env vars via pydantic-settings
│   └── database.py      # async sqlalchemy engine
├── api/
│   ├── ingest.py        # POST /ingest/
│   └── chat.py          # POST /chat/, DELETE /chat/{session_id}
├── services/
│   ├── chunker.py       # fixed and semantic chunking
│   ├── embedder.py      # huggingface embeddings
│   ├── vector_store.py  # qdrant operations
│   ├── retriever.py     # custom rag pipeline
│   ├── memory.py        # redis chat history
│   ├── llm.py           # groq client
│   └── booking.py       # booking detection and extraction
├── models/
│   └── db_models.py
└── schemas/
    └── schemas.py
</pre>

## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/BigyanLuitel/palm-mind-intern.git
cd palm-mind-intern
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

You'll need accounts on:

- [cloud.qdrant.io](https://cloud.qdrant.io) — free cluster
- [redis.io/try-free](https://redis.io/try-free) — free database
- [supabase.com](https://supabase.com) — free project
- [console.groq.com](https://console.groq.com) — free API key

Run the server:

```bash
uvicorn app.main:app --reload
```

Swagger UI available at `http://localhost:8000/docs`

## Usage

**Ingest a document:**

```bash
curl -X POST http://localhost:8000/ingest/ \
  -F "file=@document.pdf" \
  -F "chunk_strategy=fixed"
```

**Chat:**

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user-123", "message": "What is the probation period?"}'
```

**Book an interview** — just mention it in the chat. The system will ask for your name, email, date, and time across multiple messages and confirm once all details are collected.

**Clear session:**

```bash
curl -X DELETE http://localhost:8000/chat/user-123
```

## Notes

The chunking strategy is selectable per upload — `fixed` splits on character size with overlap, `semantic` splits on sentence and paragraph boundaries. Both are implemented manually without any text splitting libraries.

The RAG pipeline in `services/retriever.py` manually handles embedding, retrieval, prompt construction, and the LLM call — no framework abstractions.

Tables are auto-created on startup via SQLAlchemy.
