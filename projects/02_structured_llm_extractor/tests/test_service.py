import unittest
from unittest.mock import Mock

from extractor.models import ExtractedDocument
from extractor.service import ExtractionService


class ExtractionServiceTests(unittest.TestCase):
    def test_sends_trimmed_text_to_mock_provider(self) -> None:
        provider = Mock()
        provider.extract.return_value = ExtractedDocument(document_type="note")
        result = ExtractionService(provider).extract("  source text  ")
        self.assertEqual(result.document_type, "note")
        provider.extract.assert_called_once_with("source text")

    def test_rejects_blank_input_without_provider_call(self) -> None:
        provider = Mock()
        with self.assertRaises(ValueError):
            ExtractionService(provider).extract("   ")
        provider.extract.assert_not_called()
