from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "palm-mind-collection"
    
    redis_host: str
    redis_port: int = 19771
    redis_password: str
    
    supabase_db_url: str
    
    groq_api_key: str
    groq_model : str = "llama-3.3-70b-versatile"
    
    embedding_model : str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim : int = 384
    
    retrieval_top_k : int = 5
    chat_history_length : int = 10
    
    fixed_chunk_size : int = 512
    fixed_chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()