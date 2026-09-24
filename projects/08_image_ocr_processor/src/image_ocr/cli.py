from __future__ import annotations

import argparse
import json
from pathlib import Path

from .processor import process_image_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OCR and classify an image."
    )

    parser.add_argument(
        "image",
        type=Path,
        help="Path to the image file.",
    )

    parser.add_argument(
        "--classify",
        action="store_true",
        help="Run document classification.",
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
        result = process_image_json(
            image_path=args.image,
            classify=args.classify,
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
            print(f"JSON written to: {args.output}")
        else:
            print(output)

        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())