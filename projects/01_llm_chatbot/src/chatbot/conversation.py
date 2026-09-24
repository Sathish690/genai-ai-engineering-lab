"""Short-lived, in-memory conversation history."""

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str

    def as_api_message(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class ConversationHistory:
    """Keeps the newest complete user/assistant turns only."""

    def __init__(self, max_turns: int) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self._max_turns = max_turns
        self._messages: list[Message] = []

    def add_turn(self, user_text: str, assistant_text: str) -> None:
        self._messages.extend([Message("user", user_text), Message("assistant", assistant_text)])
        self._messages = self._messages[-(self._max_turns * 2):]

    def as_api_messages(self) -> list[dict[str, str]]:
        return [message.as_api_message() for message in self._messages]

    def clear(self) -> None:
        self._messages.clear()
