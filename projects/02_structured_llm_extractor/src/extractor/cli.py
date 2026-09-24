"""Command-line entry point for structured document extraction."""

import argparse

from dotenv import load_dotenv

from .config import ConfigurationError, Settings
from .provider import OpenAIExtractionProvider, ProviderError
from .service import ExtractionService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract validated JSON from unstructured text.")
    parser.add_argument("text", nargs="?", help="Text to extract. If omitted, it is requested interactively.")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    try:
        text = args.text if args.text is not None else input("Text to extract: ")
        settings = Settings.from_environment()
        service = ExtractionService(OpenAIExtractionProvider(settings.api_key, settings.model))
        print(service.extract(text).model_dump_json(indent=2))
    except (ConfigurationError, ProviderError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
