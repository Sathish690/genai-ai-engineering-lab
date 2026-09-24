import unittest

from rag_qa.models import Chunk, DocumentPage, RetrievedChunk
from rag_qa.prompts import NOT_FOUND
from rag_qa.service import RagService


class FakeEmbedder:
    def __init__(self) -> None: self.calls: list[list[str]] = []
    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts); return [[float(len(text))] for text in texts]


class FakeStore:
    def __init__(self, results: list[RetrievedChunk]) -> None: self.results, self.added = results, []
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: self.added.extend(zip(chunks, embeddings))
    def search(self, embedding: list[float], limit: int) -> list[RetrievedChunk]: return self.results[:limit]


class FakeGenerator:
    def __init__(self) -> None: self.prompt = ""
    def answer(self, prompt: str) -> str: self.prompt = prompt; return "Grounded answer"


class RagServiceTests(unittest.TestCase):
    def test_indexes_chunks_with_fake_embeddings(self) -> None:
        store, embedder = FakeStore([]), FakeEmbedder()
        service = RagService(embedder, store, FakeGenerator(), 8, 2, 2, 0.2)
        self.assertEqual(service.index([DocumentPage("abcdefghij", "a.txt", 1)]), 2)
        self.assertEqual(len(store.added), 2)

    def test_returns_sources_and_builds_prompt_from_retrieved_context(self) -> None:
        result = RetrievedChunk(Chunk("a", "The fee is $5.", "fees.txt", 1, 0, 0, 14), 0.9)
        generator = FakeGenerator()
        answer = RagService(FakeEmbedder(), FakeStore([result]), generator, 8, 2, 2, 0.5).ask("What is the fee?")
        self.assertEqual(answer.text, "Grounded answer")
        self.assertEqual(answer.sources, [result])
        self.assertIn("fees.txt", generator.prompt)

    def test_returns_not_found_without_relevant_context(self) -> None:
        weak = RetrievedChunk(Chunk("a", "Unrelated", "a.txt", 1, 0, 0, 9), 0.1)
        answer = RagService(FakeEmbedder(), FakeStore([weak]), FakeGenerator(), 8, 2, 1, 0.5).ask("Question")
        self.assertEqual(answer.text, NOT_FOUND)
        self.assertEqual(answer.sources, [])

    def test_rejects_blank_question(self) -> None:
        with self.assertRaises(ValueError): RagService(FakeEmbedder(), FakeStore([]), FakeGenerator(), 8, 2, 1, 0.5).ask(" ")
