from __future__ import annotations

from pathlib import Path
from typing import Any

from openai import OpenAI

from .comparator import compare_extractions
from .ocr_adapter import extract_ocr_document
from .vision_extractor import extract_with_vision
from .models import MultimodalResult


SUPPORTED_IMAGE_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
}


def validate_document(
    document_path: str | Path,
) -> Path:
    """Validate the multimodal document input."""

    path = Path(document_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Document path is not a file: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported document format: {path.suffix}"
        )

    return path


def process_document(
    document_path: str | Path,
    client: OpenAI | None = None,
    model: str | None = None,
) -> MultimodalResult:
    """
    Run the complete multimodal document pipeline.

    Pipeline:
        Image validation
        -> OCR extraction
        -> Multimodal vision extraction
        -> Comparison
        -> Structured final result
    """

    path = validate_document(document_path)

    # Step 1: OCR extraction.
    ocr_result = extract_ocr_document(path)

    # Step 2: Multimodal vision extraction.
    vision_result = extract_with_vision(
        image_path=path,
        client=client,
        model=model,
    )

    # Step 3: Compare OCR and multimodal results.
    comparison = compare_extractions(
        vision=vision_result,
        ocr=ocr_result,
    )

    # Step 4: Final structured result.
    return MultimodalResult(
        filename=path.name,
        vision=vision_result,
        ocr=ocr_result,
        comparison=comparison,
        metadata={
            "pipeline": [
                "image_validation",
                "ocr",
                "multimodal_vision",
                "comparison",
            ],
            "source_file": path.name,
        },
    )


def process_document_json(
    document_path: str | Path,
    client: OpenAI | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Run the pipeline and return JSON-compatible output."""

    result = process_document(
        document_path=document_path,
        client=client,
        model=model,
    )

    return result.model_dump()