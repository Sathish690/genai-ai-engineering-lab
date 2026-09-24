import math
import re
from typing import Protocol

from rank_bm25 import BM25Okapi

from .models import Document, SearchResult


def tokens(text: str) -> list[str]:
    """Convert text into lowercase word tokens."""
    return re.findall(r"\w+", text.lower())


class Embedder(Protocol):
    """Interface for embedding providers."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class Retriever(Protocol):
    """Common interface for retrievers."""

    def search(self, question: str, top_k: int) -> list[SearchResult]:
        ...


class BM25Retriever:
    """Keyword-based BM25 retriever."""

    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents
        self._index = BM25Okapi(
            [tokens(document.text) for document in documents]
        )

    def search(self, question: str, top_k: int) -> list[SearchResult]:
        """Return the top-k BM25-ranked documents."""
        if top_k < 1:
            return []

        query_tokens = tokens(question)

        if not query_tokens:
            return []

        scores = self._index.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores),
            key=lambda item: item[1],
            reverse=True,
        )[:top_k]

        # Do not filter by score > 0.
        # BM25 can legitimately return zero/negative scores,
        # especially with small datasets. The test and hybrid
        # retrieval logic expect the top-ranked documents to remain
        # available regardless of score sign.
        return [
            SearchResult(
                self._documents[index],
                float(score),
                "bm25",
            )
            for index, score in ranked
        ]


class VectorRetriever:
    """Vector similarity retriever using cosine similarity."""

    def __init__(
        self,
        documents: list[Document],
        embedder: Embedder,
    ) -> None:
        self._documents = documents
        self._embedder = embedder
        self._vectors = embedder.embed(
            [document.text for document in documents]
        )

    def search(self, question: str, top_k: int) -> list[SearchResult]:
        """Return the top-k documents ranked by cosine similarity."""
        if top_k < 1:
            return []

        query = self._embedder.embed([question])[0]

        def cosine(vector: list[float]) -> float:
            query_magnitude = math.sqrt(
                sum(value * value for value in query)
            )
            vector_magnitude = math.sqrt(
                sum(value * value for value in vector)
            )

            denominator = query_magnitude * vector_magnitude

            if denominator == 0:
                return 0.0

            return sum(
                a * b for a, b in zip(query, vector)
            ) / denominator

        ranked = sorted(
            zip(self._documents, self._vectors),
            key=lambda item: cosine(item[1]),
            reverse=True,
        )[:top_k]

        return [
            SearchResult(
                document,
                cosine(vector),
                "vector",
            )
            for document, vector in ranked
        ]


def reciprocal_rank_fusion(
    result_sets: list[list[SearchResult]],
    top_k: int,
    constant: int = 60,
) -> list[SearchResult]:
    """Fuse multiple ranked result sets using Reciprocal Rank Fusion."""

    if top_k < 1:
        raise ValueError("top_k must be positive.")

    if constant < 0:
        raise ValueError(
            "RRF constant cannot be negative."
        )

    totals: dict[str, tuple[Document, float]] = {}

    for results in result_sets:
        for rank, result in enumerate(results, start=1):
            document, score = totals.get(
                result.document.id,
                (result.document, 0.0),
            )

            totals[result.document.id] = (
                document,
                score + 1 / (constant + rank),
            )

    ranked_results = sorted(
        totals.values(),
        key=lambda item: item[1],
        reverse=True,
    )[:top_k]

    return [
        SearchResult(
            document,
            score,
            "rrf",
        )
        for document, score in ranked_results
    ]