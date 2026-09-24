from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from .models import DocumentResult, PageContent


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph boundaries."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove trailing spaces from each line.
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Collapse repeated spaces/tabs.
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph boundaries but remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pdf(pdf_path: str | Path) -> DocumentResult:
    """
    Extract text and metadata from a PDF.

    Raises:
        FileNotFoundError: PDF does not exist.
        ValueError: Invalid file type, invalid PDF, or protected PDF.
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Input file must have a .pdf extension.")

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        raise ValueError(
            f"Unable to read PDF: {path.name}"
        ) from exc

    # Handle encrypted/password-protected PDFs.
    if reader.is_encrypted:
        try:
            decrypted = reader.decrypt("")
        except Exception:
            decrypted = 0

        if not decrypted:
            raise ValueError(
                "The PDF is password-protected or could not be decrypted."
            )

    metadata: dict[str, Any] = {}

    if reader.metadata:
        for key, value in reader.metadata.items():
            metadata[str(key)] = (
                str(value) if value is not None else None
            )

    pages: list[PageContent] = []

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            raw_text = page.extract_text() or ""
        except Exception:
            raw_text = ""

        pages.append(
            PageContent(
                page_number=page_number,
                text=normalize_text(raw_text),
            )
        )

    has_extractable_text = any(
        page.text.strip()
        for page in pages
    )

    return DocumentResult(
        filename=path.name,
        page_count=len(pages),
        has_extractable_text=has_extractable_text,
        metadata=metadata,
        pages=pages,
    )


def extract_pdf_json(pdf_path: str | Path) -> dict[str, Any]:
    """Extract a PDF and return JSON-serializable data."""
    return extract_pdf(pdf_path).to_dict()