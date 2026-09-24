"""Pydantic models for extracted records."""

from datetime import date as CalendarDate

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExtractedDocument(BaseModel):
    """The complete, deliberately nullable extraction result."""

    model_config = ConfigDict(extra="forbid")

    document_type: str | None = None
    customer_name: str | None = None
    date: CalendarDate | None = None
    amount: float | None = None
    entities: list[str] = Field(default_factory=list)
    confidence_notes: list[str] = Field(default_factory=list)

    @field_validator("document_type", "customer_name", mode="before")
    @classmethod
    def blank_text_is_missing(cls, value: object) -> object:
        """Normalize blank optional text to null instead of pretending it has content."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("entities", "confidence_notes")
    @classmethod
    def remove_blank_list_items(cls, values: list[str]) -> list[str]:
        """Retain only meaningful list entries."""
        return [value.strip() for value in values if value.strip()]
