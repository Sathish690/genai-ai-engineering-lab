from typing import Any

from pydantic import BaseModel, Field


class OCRResult(BaseModel):
    """Structured OCR result for an image."""

    filename: str
    text: str
    confidence_notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentClassification(BaseModel):
    """Optional document classification result."""

    document_type: str
    confidence_notes: str = ""


class ImageProcessResult(BaseModel):
    """Complete image OCR processing result."""

    filename: str
    width: int
    height: int
    format: str
    size_bytes: int
    ocr: OCRResult
    classification: DocumentClassification | None = None