from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from .models import ExtractedField, VisionExtraction


SUPPORTED_IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
}


SYSTEM_PROMPT = """
You are a document information extraction assistant.

Analyze the supplied document image and extract only information that
is visible in the image.

Rules:
- Never invent missing values.
- Use null when a field is not visible.
- Identify the document type.
- Extract useful fields as name/value/evidence records.
- Evidence must describe or quote the visible text supporting the value.
- Keep the result concise.
- Return valid JSON matching the supplied schema.
""".strip()


def image_to_data_url(image_path: str | Path) -> str:
    """Convert an image file into a base64 data URL."""

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    mime_type = SUPPORTED_IMAGE_TYPES.get(
        path.suffix.lower()
    )

    if not mime_type:
        raise ValueError(
            f"Unsupported image format: {path.suffix}"
        )

    data = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime_type};base64,{data}"


def build_schema() -> dict[str, Any]:
    """Return the JSON schema expected from the multimodal model."""

    schema = VisionExtraction.model_json_schema()

    return {
        "type": "json_schema",
        "name": "vision_document_extraction",
        "strict": True,
        "schema": schema,
    }


def extract_with_vision(
    image_path: str | Path,
    client: OpenAI | None = None,
    model: str | None = None,
) -> VisionExtraction:
    """
    Extract structured information from a document image
    using a multimodal LLM.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if client is None:
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required "
                "for live multimodal extraction."
            )

        client = OpenAI(api_key=api_key)

    selected_model = model or os.getenv("OPENAI_MODEL")

    if not selected_model:
        raise ValueError(
            "OPENAI_MODEL environment variable is required."
        )

    data_url = image_to_data_url(image_path)

    response = client.responses.create(
        model=selected_model,
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze this document image and "
                            "extract the visible information."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": data_url,
                        "detail": "high",
                    },
                ],
            }
        ],
        text={
            "format": build_schema(),
        },
    )

    output_text = response.output_text

    if not output_text:
        raise RuntimeError(
            "The multimodal model returned no output."
        )

    try:
        raw_result = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "The multimodal model returned invalid JSON."
        ) from exc

    try:
        result = VisionExtraction.model_validate(
            raw_result
        )
    except Exception as exc:
        raise ValueError(
            "The multimodal model returned JSON that "
            "does not match the expected schema."
        ) from exc

    result.raw_response = output_text

    return result