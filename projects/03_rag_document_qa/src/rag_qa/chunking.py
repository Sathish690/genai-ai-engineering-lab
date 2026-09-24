"""Deterministic overlapping text chunking."""

from .models import Chunk, DocumentPage


def chunk_pages(pages: list[DocumentPage], chunk_size: int, overlap: int) -> list[Chunk]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size.")
    chunks: list[Chunk] = []
    for page in pages:
        start = 0
        index = 0
        while start < len(page.text):
            end = min(start + chunk_size, len(page.text))
            text = page.text[start:end]
            chunks.append(Chunk(f"{page.source_filename}:{page.page_number}:{index}", text, page.source_filename,
                                page.page_number, index, start, end))
            if end == len(page.text):
                break
            start = end - overlap
            index += 1
    return chunks
