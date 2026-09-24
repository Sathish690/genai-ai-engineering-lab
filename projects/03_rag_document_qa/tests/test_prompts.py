import unittest

from rag_qa.models import Chunk, RetrievedChunk
from rag_qa.prompts import NOT_FOUND, build_prompt, format_context


class PromptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = RetrievedChunk(Chunk("id", "Policy ends after 30 days.", "policy.pdf", 2, 3, 100, 130), 0.8)

    def test_formats_retrieval_with_complete_metadata(self) -> None:
        context = format_context([self.result])
        self.assertIn("source=policy.pdf", context)
        self.assertIn("page=2", context)
        self.assertIn("chunk=3", context)

    def test_prompt_is_context_only_and_includes_question(self) -> None:
        prompt = build_prompt("When does it end?", [self.result])
        self.assertIn("only the retrieved context", prompt)
        self.assertIn(NOT_FOUND, prompt)
        self.assertIn("When does it end?", prompt)
