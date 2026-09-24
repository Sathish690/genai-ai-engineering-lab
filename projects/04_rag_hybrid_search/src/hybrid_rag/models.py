from dataclasses import dataclass

@dataclass(frozen=True)
class Document:
    id: str
    text: str
    source: str

@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float
    retriever: str

@dataclass(frozen=True)
class Answer:
    text: str
    results: list[SearchResult]
