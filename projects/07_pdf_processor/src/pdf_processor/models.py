from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class PageContent:
    """Normalized content for one PDF page."""

    page_number: int
    text: str


@dataclass
class DocumentResult:
    """Normalized PDF extraction result."""

    filename: str
    page_count: int
    has_extractable_text: bool
    metadata: dict[str, Any]
    pages: list[PageContent]

    def to_dict(self) -> dict[str, Any]:
        """Convert the result into JSON-serializable data."""
        return asdict(self)