from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from rag_qa.providers import OpenAIAnswerGenerator, OpenAIEmbedder, ProviderError


class ProviderTests(unittest.TestCase):
    def test_mocked_embedding_client_returns_vectors(self) -> None:
        client = Mock(); client.embeddings.create.return_value = SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 2.0])])
        vectors = OpenAIEmbedder("not-a-real-key", "test-embedding", client).embed(["text"])
        self.assertEqual(vectors, [[1.0, 2.0]])
        client.embeddings.create.assert_called_once_with(model="test-embedding", input=["text"])

    def test_mocked_answer_client_returns_text_and_wraps_failure(self) -> None:
        client = Mock(); client.responses.create.return_value = SimpleNamespace(output_text=" Answer ")
        generator = OpenAIAnswerGenerator("not-a-real-key", "test-chat", client)
        self.assertEqual(generator.answer("prompt"), "Answer")
        client.responses.create.side_effect = RuntimeError("offline")
        with self.assertRaises(ProviderError): generator.answer("prompt")
