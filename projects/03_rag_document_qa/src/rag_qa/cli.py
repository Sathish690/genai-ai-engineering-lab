"""CLI for indexing documents and asking grounded questions."""

import argparse
from pathlib import Path
from dotenv import load_dotenv
from .config import ConfigurationError, Settings
from .loader import DocumentLoadError, load_directory
from .providers import OpenAIAnswerGenerator, OpenAIEmbedder, ProviderError
from .service import RagService
from .store import ChromaVectorStore

def main() -> int:
    parser = argparse.ArgumentParser(description="Local PDF/TXT/Markdown RAG Q&A")
    commands = parser.add_subparsers(dest="command", required=True)
    index = commands.add_parser("index"); index.add_argument("path", type=Path)
    ask = commands.add_parser("ask"); ask.add_argument("question")
    args = parser.parse_args(); load_dotenv()
    try:
        settings = Settings.from_environment()
        service = RagService(OpenAIEmbedder(settings.api_key, settings.embedding_model), ChromaVectorStore(settings.store_path),
                             OpenAIAnswerGenerator(settings.api_key, settings.chat_model), settings.chunk_size, settings.overlap, settings.top_k, settings.min_score)
        if args.command == "index": print(f"Indexed {service.index(load_directory(args.path))} chunks.")
        else:
            answer = service.ask(args.question); print(answer.text)
            for source in answer.sources: print(f"- {source.chunk.source_filename}, page {source.chunk.page_number}, chunk {source.chunk.chunk_index}, score {source.score:.3f}")
    except (ConfigurationError, DocumentLoadError, ProviderError, ValueError, RuntimeError) as error:
        print(f"Error: {error}"); return 1
    return 0

if __name__ == "__main__": raise SystemExit(main())
