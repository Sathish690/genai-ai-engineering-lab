from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ocr import ocr_pdf
from .processor import extract_pdf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract text and metadata from a PDF."
    )

    parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF file.",
    )

    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Run OCR on the PDF pages.",
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
        if args.ocr:
            result = extract_pdf(args.pdf)
            ocr_pages = ocr_pdf(args.pdf)

            for page, text in zip(result.pages, ocr_pages):
                page.text = text

            result.has_extractable_text = any(
                page.text.strip() for page in result.pages
            )

            data = result.to_dict()
        else:
            data = extract_pdf(args.pdf).to_dict()

        output = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

        if args.output:
            args.output.write_text(
                output,
                encoding="utf-8",
            )
            print(f"JSON written to: {args.output}")
        else:
            print(output)

        return 0

    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())