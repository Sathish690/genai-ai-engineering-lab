from __future__ import annotations

from pathlib import Path

import pymupdf
import pytesseract


def ocr_pdf(
    pdf_path: str | Path,
    dpi: int = 200,
) -> list[str]:
    """
    OCR each page of a scanned PDF.

    PyMuPDF renders PDF pages to images.
    Tesseract extracts text from those images.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Input file must have a .pdf extension."
        )

    try:
        document = pymupdf.open(str(path))
    except Exception as exc:
        raise ValueError(
            f"Unable to open PDF: {path.name}"
        ) from exc

    scale = dpi / 72.0
    matrix = pymupdf.Matrix(
        scale,
        scale,
    )

    pages: list[str] = []

    try:
        for page in document:
            pixmap = page.get_pixmap(
                matrix=matrix
            )

            image = pixmap.pil_image()

            text = pytesseract.image_to_string(
                image
            )

            pages.append(text.strip())

    finally:
        document.close()

    return pages