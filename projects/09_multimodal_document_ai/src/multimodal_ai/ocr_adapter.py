from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import pytesseract
from PIL import Image

from .models import ExtractedField, OCRExtraction


DEFAULT_TESSERACT_CMD = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

DEFAULT_TESSDATA_PREFIX = (
    r"E:\tesseract_18\tessdata"
)


def configure_tesseract() -> None:
    """Configure the Tesseract executable and language data."""

    configured_cmd = os.getenv("TESSERACT_CMD")

    if configured_cmd and Path(configured_cmd).exists():
        pytesseract.pytesseract.tesseract_cmd = configured_cmd

    else:
        detected = shutil.which("tesseract")

        if detected:
            pytesseract.pytesseract.tesseract_cmd = detected

        elif Path(DEFAULT_TESSERACT_CMD).exists():
            pytesseract.pytesseract.tesseract_cmd = (
                DEFAULT_TESSERACT_CMD
            )

        else:
            raise RuntimeError(
                "Tesseract executable was not found."
            )

    tessdata = os.getenv(
        "TESSDATA_PREFIX",
        DEFAULT_TESSDATA_PREFIX,
    )

    tessdata_path = Path(tessdata)

    if not tessdata_path.exists():
        raise RuntimeError(
            f"Tesseract language-data directory was not found: "
            f"{tessdata_path}"
        )

    eng_file = tessdata_path / "eng.traineddata"

    if not eng_file.exists():
        raise RuntimeError(
            f"English Tesseract language file was not found: "
            f"{eng_file}"
        )

    os.environ["TESSDATA_PREFIX"] = str(
        tessdata_path
    )


def extract_ocr_text(image_path: str | Path) -> str:
    """Run Tesseract OCR on an image."""

    configure_tesseract()

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    try:
        image = Image.open(path)
        image.load()
    except Exception as exc:
        raise ValueError(
            f"Unable to open image: {path.name}"
        ) from exc

    try:
        return pytesseract.image_to_string(
            image,
            lang="eng",
        ).strip()

    except Exception as exc:
        raise RuntimeError(
            "Tesseract OCR failed."
        ) from exc


def first_match(
    patterns: tuple[str, ...],
    text: str,
) -> str | None:
    """Return the first regex match captured by the supplied patterns."""

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            return match.group(1).strip()

    return None


def classify_ocr_text(text: str) -> str:
    """Infer a simple document type from OCR text."""

    normalized = text.lower()

    if "invoice" in normalized:
        return "invoice"

    if "receipt" in normalized:
        return "receipt"

    if (
        "application form" in normalized
        or "please fill" in normalized
    ):
        return "form"

    if (
        "passport" in normalized
        or "aadhaar" in normalized
        or "identity" in normalized
    ):
        return "id-like document"

    return "unknown"


def parse_ocr_fields(
    text: str,
) -> list[ExtractedField]:
    """Extract common invoice/document fields from OCR text."""

    fields: list[ExtractedField] = []

    invoice_number = first_match(
        (
            r"invoice\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Za-z0-9\-]+)",
            r"inv\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Za-z0-9\-]+)",
        ),
        text,
    )

    customer_name = first_match(
        (
            r"customer\s*(?:name)?\s*[:\-]\s*(.+)",
            r"bill\s*to\s*[:\-]\s*(.+)",
        ),
        text,
    )

    amount = first_match(
        (
            r"total\s*(?:amount)?\s*[:\-]?\s*([₹$€£]?\s*[\d,]+(?:\.\d{1,2})?)",
            r"amount\s*[:\-]?\s*([₹$€£]?\s*[\d,]+(?:\.\d{1,2})?)",
        ),
        text,
    )

    date = first_match(
        (
            r"date\s*[:\-]\s*([0-9]{1,4}[\/\-][0-9]{1,2}[\/\-][0-9]{1,4})",
        ),
        text,
    )

    candidates = (
        ("invoice_number", invoice_number),
        ("customer_name", customer_name),
        ("amount", amount),
        ("date", date),
    )

    for field_name, value in candidates:
        if value is not None:
            fields.append(
                ExtractedField(
                    name=field_name,
                    value=value,
                    evidence=value,
                )
            )

    return fields


def extract_ocr_document(
    image_path: str | Path,
) -> OCRExtraction:
    """
    Run OCR and convert the result into structured OCR extraction.
    """

    text = extract_ocr_text(image_path)

    document_type = classify_ocr_text(text)

    fields = parse_ocr_fields(text)

    return OCRExtraction(
        document_type=document_type,
        fields=fields,
        raw_text=text,
    )