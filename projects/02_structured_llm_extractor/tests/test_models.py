import unittest
from datetime import date

from pydantic import ValidationError

from extractor.models import ExtractedDocument


class ExtractedDocumentTests(unittest.TestCase):
    def test_accepts_complete_valid_record(self) -> None:
        document = ExtractedDocument(
            document_type="invoice", customer_name="Ava", date="2026-04-10", amount=12.5,
            entities=["Ava"], confidence_notes=[]
        )
        self.assertEqual(document.date, date(2026, 4, 10))
        self.assertEqual(document.amount, 12.5)

    def test_defaults_preserve_missing_values(self) -> None:
        document = ExtractedDocument()
        self.assertIsNone(document.document_type)
        self.assertEqual(document.entities, [])

    def test_rejects_invalid_date_and_unexpected_field(self) -> None:
        with self.assertRaises(ValidationError):
            ExtractedDocument(date="April sometime")
        with self.assertRaises(ValidationError):
            ExtractedDocument(unverified="value")

    def test_normalizes_blank_optional_text_and_list_items(self) -> None:
        document = ExtractedDocument(customer_name="  ", entities=[" Ava ", " "], confidence_notes=[" unsure "])
        self.assertIsNone(document.customer_name)
        self.assertEqual(document.entities, ["Ava"])
        self.assertEqual(document.confidence_notes, ["unsure"])
