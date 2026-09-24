from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from extractor.models import ExtractedDocument
from extractor.provider import EXTRACTION_INSTRUCTIONS, OpenAIExtractionProvider, ProviderError


class OpenAIExtractionProviderTests(unittest.TestCase):
    def test_sends_text_to_mocked_structured_responses_api(self) -> None:
        client = Mock()
        client.responses.parse.return_value = SimpleNamespace(output_parsed=ExtractedDocument(document_type="invoice"))
        result = OpenAIExtractionProvider("not-a-real-key", "test-model", client=client).extract("invoice text")
        self.assertEqual(result.document_type, "invoice")
        client.responses.parse.assert_called_once_with(
            model="test-model", instructions=EXTRACTION_INSTRUCTIONS, input="invoice text", text_format=ExtractedDocument
        )

    def test_validates_mocked_mapping_response(self) -> None:
        client = Mock()
        client.responses.parse.return_value = SimpleNamespace(output_parsed={"date": "2026-04-10", "entities": ["Ava"]})
        result = OpenAIExtractionProvider("not-a-real-key", "test-model", client=client).extract("text")
        self.assertEqual(result.model_dump(mode="json")["date"], "2026-04-10")

    def test_rejects_empty_or_invalid_mocked_responses(self) -> None:
        client = Mock()
        provider = OpenAIExtractionProvider("not-a-real-key", "test-model", client=client)
        client.responses.parse.return_value = SimpleNamespace(output_parsed=None)
        with self.assertRaises(ProviderError):
            provider.extract("text")
        client.responses.parse.return_value = SimpleNamespace(output_parsed={"date": "not-a-date"})
        with self.assertRaises(ProviderError):
            provider.extract("text")

    def test_wraps_mocked_sdk_failure(self) -> None:
        client = Mock()
        client.responses.parse.side_effect = RuntimeError("network problem")
        with self.assertRaises(ProviderError):
            OpenAIExtractionProvider("not-a-real-key", "test-model", client=client).extract("text")
