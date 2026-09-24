# Beginner-Friendly Python LLM Chatbot

## Problem

Build a small command-line chatbot that can hold a short conversation with an LLM while keeping credentials out of the source code.

## Architecture

```text
CLI -> Chatbot service -> OpenAI provider -> OpenAI Responses API
                    |
                    -> short in-memory conversation history
```

`src/chatbot/provider.py` is the only module that knows about the OpenAI SDK. The CLI and service depend on its small provider interface instead.

## Features

- Interactive terminal chat with `exit`, `quit`, and `clear` commands
- Configurable system prompt and model
- Short, in-memory conversation history
- Environment-variable credentials
- Helpful setup and API error messages
- Type hints and mocked unit tests

## Tech Stack

- Python 3.10+
- Official `openai` Python SDK and the Responses API
- `python-dotenv` for local `.env` files
- Standard-library `unittest` for tests

## Setup

From this directory, create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` to your own key. Do not commit `.env`.

## Run

```powershell
$env:PYTHONPATH = "src"
python -m chatbot.cli
```

Optional flags override environment settings:

```powershell
python -m chatbot.cli --system-prompt "You are a concise study helper." --history-turns 4
```

## Example

```text
You: What is a vector database?
Assistant: A vector database stores embeddings so applications can find semantically similar content.
You: clear
Conversation cleared.
You: exit
Goodbye!
```

## Testing

Tests mock the provider client and never make a real API call:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## Limitations

- Conversation history is lost when the program exits.
- There is no streaming, web UI, authentication layer, or content moderation.
- The selected model and API usage may incur provider charges.

## Security

- API keys are read from `OPENAI_API_KEY`; they are never hard-coded.
- `.env` is ignored by Git, while `.env.example` contains only blanks.
- Do not send sensitive, customer, or private content to an LLM without appropriate approval and data controls.

## Future Improvements

- Add streaming responses and a web interface.
- Persist opt-in, encrypted conversation sessions.
- Add retries, rate-limit handling, moderation, and telemetry.
- Add support for other providers through new provider modules.
