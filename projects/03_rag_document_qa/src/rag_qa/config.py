"""Environment settings for the RAG application."""

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError): pass


@dataclass(frozen=True)
class Settings:
    api_key: str; chat_model: str; embedding_model: str; chunk_size: int; overlap: int; top_k: int; min_score: float; store_path: Path

    @classmethod
    def from_environment(cls) -> "Settings":
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key: raise ConfigurationError("OPENAI_API_KEY is not set.")
        try:
            result = cls(key, os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini").strip(), os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip(),
                         int(os.getenv("RAG_CHUNK_SIZE", "1000")), int(os.getenv("RAG_CHUNK_OVERLAP", "200")), int(os.getenv("RAG_TOP_K", "4")),
                         float(os.getenv("RAG_MIN_SCORE", "0.25")), Path(os.getenv("RAG_STORE_PATH", ".rag_store")))
        except ValueError as error: raise ConfigurationError("RAG numeric settings are invalid.") from error
        if not result.chat_model or not result.embedding_model or result.chunk_size < 1 or result.overlap < 0 or result.overlap >= result.chunk_size or result.top_k < 1 or not 0 <= result.min_score <= 1:
            raise ConfigurationError("RAG settings are out of range or blank.")
        return result
