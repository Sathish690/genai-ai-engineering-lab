from pathlib import Path

import pytest

from multimodal_ai import processor
from multimodal_ai.models import (
    ExtractedField,
    OCRExtraction,
    VisionExtraction,
)


def create_sample_image(path: Path) -> None:
    """Create a small valid PNG image."""
    from PIL import Image

    image = Image.new(
        "RGB",
        (100, 100),
        "white",
    )
    image.save(path, format="PNG")


def test_validate_document_accepts_supported_image(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "sample.png"
    create_sample_image(image_path)

    result = processor.validate_document(
        image_path
    )

    assert result == image_path


def test_validate_document_rejects_missing_file(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        processor.validate_document(image_path)


def test_validate_document_rejects_unsupported_format(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "not an image",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported document format",
    ):
        processor.validate_document(file_path)


def test_process_document_with_mocked_components(
    monkeypatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "invoice.png"
    create_sample_image(image_path)

    fake_ocr = OCRExtraction(
        document_type="invoice",
        fields=[
            ExtractedField(
                name="invoice_number",
                value="INV1001",
                evidence="Invoice No: INV1001",
            ),
            ExtractedField(
                name="amount",
                value="25000",
                evidence="Total: 25000",
            ),
        ],
        raw_text="Invoice No: INV1001 Total: 25000",
    )

    fake_vision = VisionExtraction(
        document_type="invoice",
        fields=[
            ExtractedField(
                name="invoice_number",
                value="INV1001",
                evidence="Invoice No: INV1001",
            ),
            ExtractedField(
                name="amount",
                value="26000",
                evidence="Total: 26000",
            ),
        ],
        raw_response='{"document_type":"invoice"}',
    )

    monkeypatch.setattr(
        processor,
        "extract_ocr_document",
        lambda path: fake_ocr,
    )

    monkeypatch.setattr(
        processor,
        "extract_with_vision",
        lambda image_path, client=None, model=None: fake_vision,
    )

    result = processor.process_document(
        image_path,
        client=object(),
        model="test-model",
    )

    assert result.filename == "invoice.png"

    assert result.ocr.document_type == "invoice"
    assert result.vision.document_type == "invoice"

    assert result.ocr.fields[1].value == "25000"
    assert result.vision.fields[1].value == "26000"

    assert result.comparison.disagreement_count == 1

    amount_comparison = next(
        item
        for item in result.comparison.fields
        if item.field_name == "amount"
    )

    assert amount_comparison.matches is False
    assert amount_comparison.ocr_value == "25000"
    assert amount_comparison.vision_value == "26000"


def test_process_document_detects_matching_fields(
    monkeypatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "receipt.png"
    create_sample_image(image_path)

    fake_ocr = OCRExtraction(
        document_type="receipt",
        fields=[
            ExtractedField(
                name="amount",
                value="500",
                evidence="Total: 500",
            ),
        ],
        raw_text="Receipt Total: 500",
    )

    fake_vision = VisionExtraction(
        document_type="receipt",
        fields=[
            ExtractedField(
                name="amount",
                value="500",
                evidence="Total: 500",
            ),
        ],
        raw_response='{"document_type":"receipt"}',
    )

    monkeypatch.setattr(
        processor,
        "extract_ocr_document",
        lambda path: fake_ocr,
    )

    monkeypatch.setattr(
        processor,
        "extract_with_vision",
        lambda image_path, client=None, model=None: fake_vision,
    )

    result = processor.process_document(
        image_path,
        client=object(),
        model="test-model",
    )

    assert result.comparison.disagreement_count == 0

    assert all(
        item.matches
        for item in result.comparison.fields
    )


def test_process_document_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "form.png"
    create_sample_image(image_path)

    fake_ocr = OCRExtraction(
        document_type="form",
        fields=[],
        raw_text="Application Form",
    )

    fake_vision = VisionExtraction(
        document_type="form",
        fields=[],
        raw_response='{"document_type":"form"}',
    )

    monkeypatch.setattr(
        processor,
        "extract_ocr_document",
        lambda path: fake_ocr,
    )

    monkeypatch.setattr(
        processor,
        "extract_with_vision",
        lambda image_path, client=None, model=None: fake_vision,
    )

    result = processor.process_document_json(
        image_path,
        client=object(),
        model="test-model",
    )

    assert isinstance(result, dict)

    assert result["filename"] == "form.png"
    assert result["ocr"]["document_type"] == "form"
    assert result["vision"]["document_type"] == "form"

    assert "comparison" in result
    assert "metadata" in result