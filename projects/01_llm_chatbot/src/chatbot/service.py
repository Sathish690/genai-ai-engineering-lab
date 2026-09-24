"""Provider-independent chatbot behavior."""

from .conversation import ConversationHistory
from .provider import LLMProvider


class Chatbot:
    def __init__(self, provider: LLMProvider, system_prompt: str, history_turns: int = 3) -> None:
        self._provider = provider
        self._system_prompt = system_prompt
        self._history = ConversationHistory(history_turns)

    def reply(self, user_text: str) -> str:
        cleaned_text = user_text.strip()
        if not cleaned_text:
            raise ValueError("Please enter a message.")
        messages = self._history.as_api_messages() + [{"role": "user", "content": cleaned_text}]
        answer = self._provider.generate(messages, self._system_prompt)
        self._history.add_turn(cleaned_text, answer)
        return answer

    def clear_history(self) -> None:
        self._history.clear()
