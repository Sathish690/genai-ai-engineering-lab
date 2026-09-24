"""Persistent local Chroma vector-store adapter."""

from pathlib import Path
from typing import Protocol

from .models import Chunk, RetrievedChunk


class VectorStore(Protocol):
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...
    def search(self, embedding: list[float], limit: int) -> list[RetrievedChunk]: ...


class ChromaVectorStore:
    def __init__(self, path: Path, collection_name: str = "documents") -> None:
        try:
            import chromadb
        except ImportError as error:
            raise RuntimeError("chromadb is not installed. Run: pip install -r requirements.txt") from error
        self._collection = chromadb.PersistentClient(path=str(path)).get_or_create_collection(collection_name)

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Each chunk requires one embedding.")
        self._collection.upsert(ids=[chunk.id for chunk in chunks], documents=[chunk.text for chunk in chunks],
                                metadatas=[chunk.metadata() for chunk in chunks], embeddings=embeddings)

    def search(self, embedding: list[float], limit: int) -> list[RetrievedChunk]:
        result = self._collection.query(query_embeddings=[embedding], n_results=limit,
                                        include=["documents", "metadatas", "distances"])
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []
        ids = result["ids"][0] if result["ids"] else []
        return [RetrievedChunk(Chunk(identifier, text, metadata["source_filename"], metadata["page_number"],
                                     metadata["chunk_index"], metadata["start_offset"], metadata["end_offset"]),
                               1.0 / (1.0 + distance))
                for identifier, text, metadata, distance in zip(ids, documents, metadatas, distances)]
