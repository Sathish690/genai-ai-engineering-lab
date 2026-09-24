"""Provider-independent extraction workflow."""

from .models import ExtractedDocument
from .provider import ExtractionProvider


class ExtractionService:
    def __init__(self, provider: ExtractionProvider) -> None:
        self._provider = provider

    def extract(self, text: str) -> ExtractedDocument:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise ValueError("Please provide non-empty text to extract.")
        return self._provider.extract(cleaned_text)
