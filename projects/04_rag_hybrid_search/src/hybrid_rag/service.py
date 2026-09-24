from typing import Protocol
from .models import Answer, Document, SearchResult
from .retrievers import Retriever, reciprocal_rank_fusion

NOT_FOUND = "The information was not found in the retrieved documents."
class Generator(Protocol):
    def answer(self, prompt: str) -> str: ...
def build_prompt(question: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(f"[{item.document.id} | {item.document.source} | rrf={item.score:.4f}]\n{item.document.text}" for item in results)
    return f"Answer only from the context. If unsupported, say exactly: {NOT_FOUND}\n\nQuestion: {question}\n\nContext:\n{context}"
class HybridRagService:
    def __init__(self, keyword: Retriever, vector: Retriever, generator: Generator) -> None: self._keyword, self._vector, self._generator = keyword, vector, generator
    def retrieve(self, question: str, top_k: int) -> list[SearchResult]:
        if not question.strip(): raise ValueError("Question must not be blank.")
        return reciprocal_rank_fusion([self._keyword.search(question, top_k), self._vector.search(question, top_k)], top_k)
    def ask(self, question: str, top_k: int) -> Answer:
        results = self.retrieve(question, top_k)
        return Answer(self._generator.answer(build_prompt(question, results)), results) if results else Answer(NOT_FOUND, [])
