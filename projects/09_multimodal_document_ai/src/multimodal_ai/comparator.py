from __future__ import annotations

from .models import (
    ComparisonResult,
    FieldComparison,
    OCRExtraction,
    VisionExtraction,
)


def _field_map(
    fields,
) -> dict[str, str | None]:
    """Convert extracted fields into a normalized lookup map."""
    return {
        field.name.strip().lower(): field.value
        for field in fields
    }


def _normalize_value(
    value: str | None,
) -> str | None:
    """Normalize values for comparison."""
    if value is None:
        return None

    return " ".join(value.strip().lower().split())


def compare_extractions(
    vision: VisionExtraction,
    ocr: OCRExtraction,
) -> ComparisonResult:
    """
    Compare document type and extracted fields.

    A disagreement is recorded whenever the normalized values differ.
    """

    vision_fields = _field_map(vision.fields)
    ocr_fields = _field_map(ocr.fields)

    all_field_names = sorted(
        set(vision_fields) | set(ocr_fields)
    )

    comparisons: list[FieldComparison] = []

    for field_name in all_field_names:
        vision_value = vision_fields.get(field_name)
        ocr_value = ocr_fields.get(field_name)

        normalized_vision = _normalize_value(
            vision_value
        )
        normalized_ocr = _normalize_value(
            ocr_value
        )

        matches = (
            normalized_vision == normalized_ocr
        )

        comparisons.append(
            FieldComparison(
                field_name=field_name,
                vision_value=vision_value,
                ocr_value=ocr_value,
                matches=matches,
            )
        )

    # Compare document type separately.
    document_type_matches = (
        _normalize_value(vision.document_type)
        == _normalize_value(ocr.document_type)
    )

    comparisons.append(
        FieldComparison(
            field_name="document_type",
            vision_value=vision.document_type,
            ocr_value=ocr.document_type,
            matches=document_type_matches,
        )
    )

    disagreement_count = sum(
        not comparison.matches
        for comparison in comparisons
    )

    return ComparisonResult(
        fields=comparisons,
        disagreement_count=disagreement_count,
    )