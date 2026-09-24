from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from pdf_processor.processor import extract_pdf, extract_pdf_json


def create_text_pdf(path: Path, text: str) -> None:
    """Create a small synthetic PDF for testing."""
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 720, text)
    pdf.save()


def create_empty_pdf(path: Path) -> None:
    """Create a PDF containing an empty page."""
    pdf = canvas.Canvas(str(path))
    pdf.showPage()
    pdf.save()


def test_extract_normal_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    create_text_pdf(
        pdf_path,
        "Hello from the PDF processor.",
    )

    result = extract_pdf(pdf_path)

    assert result.filename == "sample.pdf"
    assert result.page_count == 1
    assert result.has_extractable_text is True
    assert len(result.pages) == 1
    assert result.pages[0].page_number == 1
    assert "Hello from the PDF processor." in result.pages[0].text


def test_extract_empty_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty.pdf"
    create_empty_pdf(pdf_path)

    result = extract_pdf(pdf_path)

    assert result.filename == "empty.pdf"
    assert result.page_count == 1
    assert result.has_extractable_text is False
    assert result.pages[0].page_number == 1
    assert result.pages[0].text == ""


def test_json_output(tmp_path: Path) -> None:
    pdf_path = tmp_path / "json_test.pdf"
    create_text_pdf(pdf_path, "JSON test content.")

    result = extract_pdf_json(pdf_path)

    assert result["filename"] == "json_test.pdf"
    assert result["page_count"] == 1
    assert result["has_extractable_text"] is True
    assert result["pages"][0]["page_number"] == 1


def test_missing_pdf_raises_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_pdf(missing_path)


def test_non_pdf_file_raises_error(tmp_path: Path) -> None:
    text_path = tmp_path / "document.txt"
    text_path.write_text("Not a PDF.", encoding="utf-8")

    with pytest.raises(ValueError, match="pdf"):
        extract_pdf(text_path)


def test_invalid_pdf_raises_error(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.pdf"
    invalid_path.write_text(
        "This is not a real PDF.",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unable to read PDF"):
        extract_pdf(invalid_path)