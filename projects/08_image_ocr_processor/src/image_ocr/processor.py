from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Final

import pytesseract
from PIL import Image, ImageOps

from .models import (
    DocumentClassification,
    ImageProcessResult,
    OCRResult,
)


# Maximum accepted image size: 10 MB
MAX_FILE_SIZE_BYTES: Final[int] = 10 * 1024 * 1024

# Image formats supported by this project
SUPPORTED_FORMATS: Final[set[str]] = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
}


def configure_tesseract() -> None:
    """
    Configure the Tesseract executable and English language data.

    Priority:
    1. TESSERACT_CMD environment variable
    2. Tesseract found on PATH
    3. Common Windows installation path

    The current system uses:
        C:\\Program Files\\Tesseract-OCR\\tesseract.exe

    Language data is located at:
        E:\\tesseract_18\\tessdata\\eng.traineddata
    """

    # Allow configuration through environment variables.
    configured_cmd = os.getenv("TESSERACT_CMD")
    configured_tessdata = os.getenv("TESSDATA_PREFIX")

    # 1. Use explicitly configured executable.
    if configured_cmd and Path(configured_cmd).exists():
        tesseract_cmd = configured_cmd

    # 2. Look for Tesseract on PATH.
    else:
        detected_cmd = shutil.which("tesseract")

        if detected_cmd:
            tesseract_cmd = detected_cmd

        # 3. Common Windows installation path.
        else:
            default_path = Path(
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

            if default_path.exists():
                tesseract_cmd = str(default_path)
            else:
                # Do not fail during module import.
                # Actual OCR will produce a clear error later.
                tesseract_cmd = None

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Configure the custom tessdata directory used on this machine.
    if configured_tessdata:
        tessdata_dir = Path(configured_tessdata)

    else:
        tessdata_dir = Path(
            r"E:\tesseract_18\tessdata"
        )

    if tessdata_dir.exists():
        os.environ["TESSDATA_PREFIX"] = str(
            tessdata_dir
        )


# Configure Tesseract when the module is imported.
configure_tesseract()


def validate_image(
    image_path: str | Path,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES,
) -> Path:
    """
    Validate image path, image type, and file size.

    Raises:
        FileNotFoundError:
            Image does not exist.

        ValueError:
            Path is not a file, unsupported format, or image
            exceeds the allowed size.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported image format: "
            f"{suffix or 'unknown'}"
        )

    file_size = path.stat().st_size

    if file_size > max_size_bytes:
        raise ValueError(
            "Image exceeds the maximum allowed size of "
            f"{max_size_bytes // (1024 * 1024)} MB."
        )

    return path


def preprocess_image(
    image: Image.Image,
) -> Image.Image:
    """
    Preprocess an image for OCR.

    Processing steps:
    1. Convert to grayscale.
    2. Resize small images.
    3. Improve contrast.
    4. Apply thresholding.
    """

    # Convert RGB/color image to grayscale.
    grayscale = ImageOps.grayscale(image)

    width, height = grayscale.size

    # Increase resolution for better OCR on small images.
    minimum_width = 1200

    if width < minimum_width:
        scale = minimum_width / width

        grayscale = grayscale.resize(
            (
                int(width * scale),
                int(height * scale),
            ),
            Image.Resampling.LANCZOS,
        )

    # Improve contrast.
    enhanced = ImageOps.autocontrast(
        grayscale
    )

    # Simple binary threshold.
    thresholded = enhanced.point(
        lambda pixel: 255 if pixel > 160 else 0
    )

    return thresholded


def classify_document(
    text: str,
) -> DocumentClassification:
    """
    Classify a document using transparent keyword heuristics.

    Supported categories:
    - invoice
    - receipt
    - form
    - id-like document
    - unknown
    """

    normalized = text.lower()

    scores = {
        "invoice": 0,
        "receipt": 0,
        "form": 0,
        "id-like document": 0,
    }

    invoice_keywords = (
        "invoice",
        "invoice number",
        "subtotal",
        "tax",
        "total amount",
        "bill to",
    )

    receipt_keywords = (
        "receipt",
        "cash",
        "change",
        "subtotal",
        "total",
    )

    form_keywords = (
        "application form",
        "form",
        "signature",
        "date of birth",
        "please fill",
    )

    id_keywords = (
        "date of birth",
        "dob",
        "identity",
        "id number",
        "passport",
        "aadhaar",
        "driving licence",
        "driver license",
    )

    for keyword in invoice_keywords:
        if keyword in normalized:
            scores["invoice"] += 1

    for keyword in receipt_keywords:
        if keyword in normalized:
            scores["receipt"] += 1

    for keyword in form_keywords:
        if keyword in normalized:
            scores["form"] += 1

    for keyword in id_keywords:
        if keyword in normalized:
            scores["id-like document"] += 1

    best_type = max(
        scores,
        key=scores.get,
    )

    best_score = scores[best_type]

    if best_score == 0:
        return DocumentClassification(
            document_type="unknown",
            confidence_notes=(
                "No strong classification keywords "
                "were detected."
            ),
        )

    return DocumentClassification(
        document_type=best_type,
        confidence_notes=(
            "Classification uses simple keyword heuristics "
            "and should be treated as approximate."
        ),
    )


def process_image(
    image_path: str | Path,
    classify: bool = False,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES,
) -> ImageProcessResult:
    """
    Validate, preprocess, OCR, and optionally classify an image.
    """

    path = validate_image(
        image_path,
        max_size_bytes=max_size_bytes,
    )

    # Open the image.
    try:
        image = Image.open(path)
        image.load()

    except Exception as exc:
        raise ValueError(
            f"Unable to open image: {path.name}"
        ) from exc

    original_format = (
        image.format
        or path.suffix.lstrip(".").upper()
    )

    width, height = image.size

    # Preprocess image before OCR.
    processed = preprocess_image(image)

    # Verify that Tesseract executable is available.
    tesseract_cmd = (
        pytesseract.pytesseract.tesseract_cmd
    )

    if not tesseract_cmd or not Path(
        tesseract_cmd
    ).exists():
        raise RuntimeError(
            "Tesseract OCR executable was not found. "
            "Expected installation at "
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            "."
        )

    # Verify English language data.
    tessdata_dir = os.getenv(
        "TESSDATA_PREFIX"
    )

    if tessdata_dir:
        eng_data = (
            Path(tessdata_dir)
            / "eng.traineddata"
        )

        if not eng_data.exists():
            raise RuntimeError(
                "English Tesseract language data was not found: "
                f"{eng_data}"
            )

    # Run OCR.
    try:
        text = pytesseract.image_to_string(
            processed
        ).strip()

    except Exception as exc:
        raise RuntimeError(
            "OCR processing failed. Verify that Tesseract "
            "OCR and the English language data are installed."
        ) from exc

    # Build OCR result.
    ocr_result = OCRResult(
        filename=path.name,
        text=text,
        confidence_notes=(
            "OCR output may contain recognition errors. "
            "Accuracy depends on image quality, resolution, "
            "layout, and text clarity."
        ),
        metadata={
            "original_format": original_format,
            "original_width": width,
            "original_height": height,
        },
    )

    # Optional classification.
    classification = (
        classify_document(text)
        if classify
        else None
    )

    return ImageProcessResult(
        filename=path.name,
        width=width,
        height=height,
        format=original_format,
        size_bytes=path.stat().st_size,
        ocr=ocr_result,
        classification=classification,
    )


def process_image_json(
    image_path: str | Path,
    classify: bool = False,
    max_size_bytes: int = MAX_FILE_SIZE_BYTES,
) -> dict:
    """
    Process an image and return JSON-compatible output.
    """

    result = process_image(
        image_path=image_path,
        classify=classify,
        max_size_bytes=max_size_bytes,
    )

    return result.model_dump()