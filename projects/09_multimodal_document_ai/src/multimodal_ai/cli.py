from __future__ import annotations

import argparse
import json
from pathlib import Path

from .processor import process_document_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multimodal document AI processor."
    )

    parser.add_argument(
        "document",
        type=Path,
        help="Path to the document image.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output file.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        result = process_document_json(
            args.document,
        )

        output = json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )

        if args.output:
            args.output.write_text(
                output,
                encoding="utf-8",
            )
            print(
                f"JSON written to: {args.output}"
            )
        else:
            print(output)

        return 0

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())