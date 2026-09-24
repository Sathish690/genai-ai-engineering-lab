"""Typed records flowing through the RAG pipeline."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentPage:
    text: str
    source_filename: str
    page_number: int


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source_filename: str
    page_number: int
    chunk_index: int
    start_offset: int
    end_offset: int

    def metadata(self) -> dict[str, int | str]:
        return {"source_filename": self.source_filename, "page_number": self.page_number,
                "chunk_index": self.chunk_index, "start_offset": self.start_offset, "end_offset": self.end_offset}


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass(frozen=True)
class Answer:
    text: str
    sources: list[RetrievedChunk]
