from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from image_ocr import processor


def create_test_image(path: Path, text: str = "INVOICE 1001") -> None:
    """Create a synthetic image for testing."""
    image = Image.new("RGB", (1200, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.text((50, 100), text, fill="black")
    image.save(path, format="PNG")


def test_validate_image_accepts_supported_format(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "sample.png"
    create_test_image(image_path)

    result = processor.validate_image(image_path)

    assert result == image_path


def test_validate_image_rejects_missing_file(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        processor.validate_image(image_path)


def test_validate_image_rejects_unsupported_format(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "not an image",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported image format"):
        processor.validate_image(file_path)


def test_validate_image_rejects_large_file(
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "large.png"
    create_test_image(image_path)

    with pytest.raises(ValueError, match="maximum allowed size"):
        processor.validate_image(
            image_path,
            max_size_bytes=1,
        )


def test_preprocess_image_converts_to_grayscale() -> None:
    image = Image.new(
        "RGB",
        (400, 200),
        "white",
    )

    processed = processor.preprocess_image(image)

    assert processed.mode == "L"
    assert processed.width >= 400
    assert processed.height >= 200


def test_process_image_with_mocked_ocr(
    monkeypatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "invoice.png"
    create_test_image(
        image_path,
        text="Invoice Total 25000",
    )

    def fake_ocr(image):
        return "Invoice Total 25000"

    monkeypatch.setattr(
        processor.pytesseract,
        "image_to_string",
        fake_ocr,
    )

    result = processor.process_image(
        image_path,
        classify=True,
    )

    assert result.filename == "invoice.png"
    assert result.width == 1200
    assert result.height == 500
    assert result.format == "PNG"
    assert result.size_bytes > 0

    assert result.ocr.text == "Invoice Total 25000"

    assert result.classification is not None
    assert result.classification.document_type == "invoice"


def test_process_image_json(
    monkeypatch,
    tmp_path: Path,
) -> None:
    image_path = tmp_path / "receipt.png"
    create_test_image(
        image_path,
        text="Receipt Total 500",
    )

    monkeypatch.setattr(
        processor.pytesseract,
        "image_to_string",
        lambda image: "Receipt Total 500",
    )

    result = processor.process_image_json(
        image_path,
        classify=True,
    )

    assert result["filename"] == "receipt.png"
    assert result["ocr"]["text"] == "Receipt Total 500"

    assert result["classification"] is not None
    assert (
        result["classification"]["document_type"]
        == "receipt"
    )


def test_classification_unknown() -> None:
    result = processor.classify_document(
        "This document contains ordinary text."
    )

    assert result.document_type == "unknown"