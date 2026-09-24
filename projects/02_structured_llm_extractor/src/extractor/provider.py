"""The sole module coupled to the OpenAI SDK."""

from typing import Any, Protocol

from .models import ExtractedDocument

EXTRACTION_INSTRUCTIONS = """Extract only facts explicitly present in the user's text.
Return the requested schema. Never guess, infer, or fabricate a missing value: use null
for document_type, customer_name, date, and amount; use [] for entities and
confidence_notes when absent. Dates must be ISO-8601 calendar dates. Include concise
confidence_notes only for material ambiguity or missing information."""


class ExtractionProvider(Protocol):
    def extract(self, text: str) -> ExtractedDocument:
        """Extract a validated record from one source text."""


class ProviderError(RuntimeError):
    """Raised when an LLM provider cannot return a valid extraction."""


class OpenAIExtractionProvider:
    """OpenAI Responses API adapter using Pydantic structured output."""

    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self._model = model
        if client is not None:
            self._client = client
            return
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ProviderError("The openai package is not installed. Run: pip install -r requirements.txt") from error
        self._client = OpenAI(api_key=api_key)

    def extract(self, text: str) -> ExtractedDocument:
        try:
            response = self._client.responses.parse(
                model=self._model,
                instructions=EXTRACTION_INSTRUCTIONS,
                input=text,
                text_format=ExtractedDocument,
            )
            parsed = response.output_parsed
            if parsed is None:
                raise ProviderError("The LLM returned no structured extraction.")
            if isinstance(parsed, ExtractedDocument):
                return parsed
            return ExtractedDocument.model_validate(parsed)
        except ProviderError:
            raise
        except Exception as error:
            raise ProviderError("The LLM extraction failed or did not match the required schema.") from error
