import json
from pathlib import Path
import unittest

from extractor.models import ExtractedDocument


class SampleDocumentTests(unittest.TestCase):
    def test_ten_samples_have_schema_valid_expected_outputs(self) -> None:
        path = Path(__file__).parents[1] / "samples" / "sample_documents.json"
        samples = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(samples), 10)
        for sample in samples:
            self.assertTrue(sample["input"].strip())
            ExtractedDocument.model_validate(sample["expected"])
