from pathlib import Path

import pytest

from pdf_processor import ocr


def test_ocr_pdf_missing_file() -> None:
    """Missing PDF should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        ocr.ocr_pdf("missing.pdf")


def test_ocr_pdf_rejects_non_pdf(tmp_path: Path) -> None:
    """Non-PDF input should be rejected."""
    text_file = tmp_path / "document.txt"
    text_file.write_text(
        "not a pdf",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="pdf"):
        ocr.ocr_pdf(text_file)


def test_ocr_pdf_processes_pages(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """OCR should process every rendered PDF page."""

    pdf_path = tmp_path / "scanned.pdf"
    pdf_path.write_bytes(b"%PDF-test")

    class FakePixmap:
        def pil_image(self):
            return "fake-image"

    class FakePage:
        def get_pixmap(self, matrix):
            return FakePixmap()

    class FakeDocument:
        def __iter__(self):
            return iter(
                [
                    FakePage(),
                    FakePage(),
                ]
            )

        def close(self):
            pass

    class FakePyMuPDF:
        class Matrix:
            def __init__(self, *args):
                pass

        @staticmethod
        def open(path):
            return FakeDocument()

    calls: list[object] = []

    def fake_image_to_string(image):
        calls.append(image)
        return f"OCR text {len(calls)}"

    # IMPORTANT:
    # ocr.py uses "import pymupdf",
    # so the test must patch "pymupdf", not "fitz".
    monkeypatch.setattr(
        ocr,
        "pymupdf",
        FakePyMuPDF,
    )

    monkeypatch.setattr(
        ocr.pytesseract,
        "image_to_string",
        fake_image_to_string,
    )

    result = ocr.ocr_pdf(pdf_path)

    assert result == [
        "OCR text 1",
        "OCR text 2",
    ]

    assert calls == [
        "fake-image",
        "fake-image",
    ]


def test_ocr_pdf_rejects_directory(
    tmp_path: Path,
) -> None:
    """A directory should be rejected."""
    directory = tmp_path / "sample.pdf"
    directory.mkdir()

    with pytest.raises(ValueError, match="not a file"):
        ocr.ocr_pdf(directory)