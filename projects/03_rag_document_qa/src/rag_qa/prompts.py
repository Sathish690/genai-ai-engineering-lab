"""Grounded prompt construction and source formatting."""

from .models import RetrievedChunk

NOT_FOUND = "The information was not found in the retrieved documents."


def format_context(results: list[RetrievedChunk]) -> str:
    return "\n\n".join(
        f"[source={result.chunk.source_filename}; page={result.chunk.page_number}; chunk={result.chunk.chunk_index}; score={result.score:.3f}]\n{result.chunk.text}"
        for result in results
    )


def build_prompt(question: str, results: list[RetrievedChunk]) -> str:
    return f"""Answer the question using only the retrieved context below. Do not use outside knowledge or infer missing facts.
If the context does not support an answer, respond exactly: {NOT_FOUND}
Answer concisely and do not invent citations.

Question: {question}

Retrieved context:
{format_context(results)}"""
