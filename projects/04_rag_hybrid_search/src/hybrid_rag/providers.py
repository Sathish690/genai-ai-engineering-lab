from typing import Any
class ProviderError(RuntimeError): pass
class OpenAIEmbedder:
    def __init__(self, key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=key)
        self._client = client
    def embed(self, texts: list[str]) -> list[list[float]]:
        try: return [item.embedding for item in self._client.embeddings.create(model=self._model, input=texts).data]
        except Exception as error: raise ProviderError("Embedding request failed.") from error
class OpenAIAnswerGenerator:
    def __init__(self, key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=key)
        self._client = client
    def answer(self, prompt: str) -> str:
        try: text = self._client.responses.create(model=self._model, input=prompt).output_text.strip()
        except Exception as error: raise ProviderError("Answer request failed.") from error
        if not text: raise ProviderError("The LLM returned an empty answer.")
        return text
