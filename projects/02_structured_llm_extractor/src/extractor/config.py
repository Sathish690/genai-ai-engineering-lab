"""Environment-based settings."""

import os
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Raised when required application configuration is unavailable."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str

    @classmethod
    def from_environment(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY is not set. Add it to .env or your environment.")

        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
        if not model:
            raise ConfigurationError("OPENAI_MODEL must not be blank.")
        return cls(api_key=api_key, model=model)
