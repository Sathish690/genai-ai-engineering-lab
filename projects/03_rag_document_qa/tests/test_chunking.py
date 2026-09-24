import unittest

from rag_qa.chunking import chunk_pages
from rag_qa.loader import clean_text
from rag_qa.models import DocumentPage


class ChunkingTests(unittest.TestCase):
    def test_cleans_whitespace_and_creates_overlapping_chunks(self) -> None:
        page = DocumentPage(clean_text(" alpha\n beta   gamma delta "), "guide.txt", 1)
        chunks = chunk_pages([page], chunk_size=10, overlap=3)
        self.assertEqual(page.text, "alpha beta gamma delta")
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[1].start_offset, chunks[0].end_offset - 3)

    def test_preserves_source_page_and_offset_metadata(self) -> None:
        chunk = chunk_pages([DocumentPage("abcdefgh", "manual.md", 4)], 5, 1)[0]
        self.assertEqual(chunk.metadata(), {"source_filename": "manual.md", "page_number": 4, "chunk_index": 0, "start_offset": 0, "end_offset": 5})

    def test_rejects_invalid_chunk_settings(self) -> None:
        with self.assertRaises(ValueError): chunk_pages([], 10, 10)
