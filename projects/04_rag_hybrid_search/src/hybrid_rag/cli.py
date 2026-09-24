import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from .config import ConfigurationError, Settings
from .evaluation import EvaluationQuestion, evaluate
from .models import Document
from .providers import OpenAIAnswerGenerator, OpenAIEmbedder, ProviderError
from .retrievers import BM25Retriever, VectorRetriever
from .service import HybridRagService

def load_documents(path: Path) -> list[Document]:
    files = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.suffix.lower() in {".txt", ".md"})
    return [Document(f"{file.name}:0", file.read_text(encoding="utf-8"), file.name) for file in files if file.read_text(encoding="utf-8").strip()]
def main() -> int:
    parser = argparse.ArgumentParser(description="Hybrid BM25 + vector RAG")
    parser.add_argument("command", choices=["index", "ask", "evaluate"]); parser.add_argument("value", nargs="?")
    parser.add_argument("--top-k", type=int); parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(); load_dotenv()
    try:
        settings = Settings.from_environment(); documents = load_documents(Path(args.value or "documents"))
        embedder = OpenAIEmbedder(settings.key, settings.embedding_model); service = HybridRagService(BM25Retriever(documents), VectorRetriever(documents, embedder), OpenAIAnswerGenerator(settings.key, settings.chat_model))
        top_k = args.top_k or settings.top_k
        if args.command == "ask":
            answer = service.ask(args.value or "", top_k); print(answer.text)
            if args.debug:
                for item in answer.results: print(f"{item.document.id} {item.retriever}={item.score:.4f} {item.document.source}")
        elif args.command == "evaluate":
            data = json.loads((Path(__file__).parents[2] / "evaluations" / "questions.json").read_text())
            report = evaluate(service, [EvaluationQuestion(**item) for item in data], top_k); print(f"Hit rate: {report.hit_rate:.1%} ({report.hits}/{report.total})")
        else: print(f"Loaded {len(documents)} documents; use ask to query the same corpus.")
    except (ConfigurationError, ProviderError, ValueError, OSError) as error: print(f"Error: {error}"); return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
