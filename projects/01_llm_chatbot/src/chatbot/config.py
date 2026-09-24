"""Configuration loaded from environment variables."""

from dataclasses import dataclass
import os


class ConfigurationError(ValueError):
    """Raised when chatbot configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    system_prompt: str
    history_turns: int

    @classmethod
    def from_environment(cls) -> "Settings":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is not set. Add it to .env or your environment."
            )

        history_text = os.getenv("CHATBOT_HISTORY_TURNS", "3")
        try:
            history_turns = int(history_text)
        except ValueError as error:
            raise ConfigurationError("CHATBOT_HISTORY_TURNS must be a whole number.") from error
        if history_turns < 1:
            raise ConfigurationError("CHATBOT_HISTORY_TURNS must be at least 1.")

        return cls(
            api_key=api_key,
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip(),
            system_prompt=os.getenv(
                "CHATBOT_SYSTEM_PROMPT", "You are a helpful, concise assistant."
            ).strip(),
            history_turns=history_turns,
        )
