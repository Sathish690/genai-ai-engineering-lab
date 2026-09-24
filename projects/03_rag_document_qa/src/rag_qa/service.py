"""RAG orchestration independent of concrete providers."""

from .chunking import chunk_pages
from .models import Answer, DocumentPage, RetrievedChunk
from .prompts import NOT_FOUND, build_prompt
from .providers import AnswerGenerator, Embedder
from .store import VectorStore


class RagService:
    def __init__(self, embedder: Embedder, store: VectorStore, generator: AnswerGenerator,
                 chunk_size: int, overlap: int, top_k: int, min_score: float) -> None:
        self._embedder, self._store, self._generator = embedder, store, generator
        self._chunk_size, self._overlap, self._top_k, self._min_score = chunk_size, overlap, top_k, min_score

    def index(self, pages: list[DocumentPage]) -> int:
        chunks = chunk_pages(pages, self._chunk_size, self._overlap)
        if chunks:
            self._store.add(chunks, self._embedder.embed([chunk.text for chunk in chunks]))
        return len(chunks)

    def ask(self, question: str) -> Answer:
        cleaned = question.strip()
        if not cleaned:
            raise ValueError("Please provide a non-empty question.")
        results = [result for result in self._store.search(self._embedder.embed([cleaned])[0], self._top_k)
                   if result.score >= self._min_score]
        if not results:
            return Answer(NOT_FOUND, [])
        return Answer(self._generator.answer(build_prompt(cleaned, results)), results)
