# Structured LLM Extractor

Extract a small, validated JSON record from unstructured text such as invoices, receipts, emails, or letters.

## Architecture

```text
CLI / text input -> ExtractionService -> ExtractionProvider -> OpenAI Responses API
                                    -> ExtractedDocument (Pydantic)
```

Only `src/extractor/provider.py` imports the OpenAI SDK. The service depends on a provider protocol, which lets tests use mocks rather than a network client. Pydantic validates the final application model even when the provider returns a parsed object.

## Output schema

Every result has these fields:

- `document_type`: string or `null`
- `customer_name`: string or `null`
- `date`: ISO-8601 date string or `null`
- `amount`: number or `null`
- `entities`: list of explicitly mentioned names, organizations, or products
- `confidence_notes`: list of concise notes about uncertainty or missing evidence

Absent information must remain `null` or an empty list. The prompt explicitly forbids guessing or completing missing values.

## Setup

Use Python 3.10+ from this project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `OPENAI_API_KEY` only in your local `.env` or shell environment. Do not commit `.env`.

## Run

Pass text as an argument:

```powershell
$env:PYTHONPATH = "src"
python -m extractor.cli "Invoice INV-100: Acme Ltd billed Priya Shah $125.50 on 2026-04-10."
```

Or omit the argument and paste text at the prompt. The command prints JSON. `OPENAI_MODEL` optionally overrides the default `gpt-4.1-mini`.

## Examples and samples

Ten input/expected-output pairs are available in [`samples/sample_documents.json`](samples/sample_documents.json). Expected values use `null` and empty lists when a source does not establish a field.

## Testing

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Tests inject mock providers or mock the SDK client. They never create a real SDK client with credentials and never make a real LLM API request.

## Validation and hallucination risks

Structured output constrains shape, but it does not prove the extracted facts are true. An LLM can still misread text, infer a value, or normalize an ambiguous date incorrectly. This application reduces that risk with an explicit no-invention prompt, nullable fields, Pydantic type checks, and `confidence_notes`; callers should still review records before consequential use.

## Security and limitations

API keys are read only from `OPENAI_API_KEY`; no secret is hard-coded. Avoid submitting sensitive text without the appropriate approval and data controls. The tool has no OCR, retrieval, human-review workflow, retry policy, or deterministic factual verification. Date parsing requires an ISO date in the model output, and a valid schema does not guarantee a correct extraction.
