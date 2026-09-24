import os
from dataclasses import dataclass
class ConfigurationError(ValueError): pass
@dataclass(frozen=True)
class Settings:
    key: str; chat_model: str; embedding_model: str; top_k: int
    @classmethod
    def from_environment(cls) -> "Settings":
        key = os.getenv("OPENAI_API_KEY", "").strip()
        if not key: raise ConfigurationError("OPENAI_API_KEY is not set.")
        try: settings = cls(key, os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini").strip(), os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip(), int(os.getenv("HYBRID_TOP_K", "4")))
        except ValueError as error: raise ConfigurationError("HYBRID_TOP_K must be a whole number.") from error
        if not settings.chat_model or not settings.embedding_model or settings.top_k < 1: raise ConfigurationError("Models must not be blank and top_k must be positive.")
        return settings
