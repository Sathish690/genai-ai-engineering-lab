from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from hybrid_rag.providers import OpenAIAnswerGenerator, OpenAIEmbedder, ProviderError
class ProviderTests(unittest.TestCase):
 def test_mock_embedding_call(self):
  client=Mock(); client.embeddings.create.return_value=SimpleNamespace(data=[SimpleNamespace(embedding=[1.0])])
  self.assertEqual(OpenAIEmbedder("not-real","model",client).embed(["x"]),[[1.0]])
 def test_mock_answer_and_error(self):
  client=Mock(); client.responses.create.return_value=SimpleNamespace(output_text=" yes "); generator=OpenAIAnswerGenerator("not-real","model",client)
  self.assertEqual(generator.answer("p"),"yes"); client.responses.create.side_effect=RuntimeError()
  with self.assertRaises(ProviderError): generator.answer("p")
