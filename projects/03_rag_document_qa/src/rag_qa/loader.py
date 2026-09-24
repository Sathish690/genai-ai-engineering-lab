"""Load text-bearing local documents into page records."""

from pathlib import Path

from .models import DocumentPage

SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md"}


class DocumentLoadError(RuntimeError):
    """Raised when a supported source cannot be read."""


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving the text's words and order."""
    return " ".join(text.replace("\x00", " ").split())


def load_path(path: Path) -> list[DocumentPage]:
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise DocumentLoadError(f"Unsupported file type: {path.name}")
    try:
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages = [DocumentPage(clean_text(page.extract_text() or ""), path.name, number)
                     for number, page in enumerate(reader.pages, start=1)]
        else:
            pages = [DocumentPage(clean_text(path.read_text(encoding="utf-8")), path.name, 1)]
    except (OSError, ValueError) as error:
        raise DocumentLoadError(f"Could not load {path.name}: {error}") from error
    return [page for page in pages if page.text]


def load_directory(path: Path) -> list[DocumentPage]:
    if not path.exists():
        raise DocumentLoadError(f"Path does not exist: {path}")
    files = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.suffix.lower() in SUPPORTED_SUFFIXES)
    pages: list[DocumentPage] = []
    for file_path in files:
        pages.extend(load_path(file_path))
    return pages
