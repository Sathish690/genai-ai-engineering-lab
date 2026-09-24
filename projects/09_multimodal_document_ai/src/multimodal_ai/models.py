from typing import Any

from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    """One extracted document field with optional evidence."""

    name: str = Field(min_length=1)
    value: str | None = None
    evidence: str | None = None


class VisionExtraction(BaseModel):
    """Structured output produced from multimodal document analysis."""

    document_type: str
    fields: list[ExtractedField] = Field(default_factory=list)
    raw_response: str | None = None


class OCRExtraction(BaseModel):
    """OCR-derived document information."""

    document_type: str
    fields: list[ExtractedField] = Field(default_factory=list)
    raw_text: str = ""


class FieldComparison(BaseModel):
    """Comparison between multimodal and OCR values."""

    field_name: str
    vision_value: str | None = None
    ocr_value: str | None = None
    matches: bool


class ComparisonResult(BaseModel):
    """Agreement/disagreement report between two extraction methods."""

    fields: list[FieldComparison] = Field(default_factory=list)
    disagreement_count: int = 0


class MultimodalResult(BaseModel):
    """Final multimodal document-processing result."""

    filename: str
    vision: VisionExtraction
    ocr: OCRExtraction
    comparison: ComparisonResult
    metadata: dict[str, Any] = Field(default_factory=dict)