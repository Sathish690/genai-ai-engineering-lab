"""Command-line entry point for the chatbot."""

import argparse

from dotenv import load_dotenv

from .config import ConfigurationError, Settings
from .provider import OpenAIProvider, ProviderError
from .service import Chatbot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat with an OpenAI model from your terminal.")
    parser.add_argument("--system-prompt", help="Override CHATBOT_SYSTEM_PROMPT.")
    parser.add_argument("--history-turns", type=int, help="Override CHATBOT_HISTORY_TURNS.")
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    try:
        settings = Settings.from_environment()
        if args.system_prompt:
            settings = Settings(settings.api_key, settings.model, args.system_prompt, settings.history_turns)
        if args.history_turns is not None:
            settings = Settings(settings.api_key, settings.model, settings.system_prompt, args.history_turns)
        chatbot = Chatbot(OpenAIProvider(settings.api_key, settings.model), settings.system_prompt, settings.history_turns)
    except (ConfigurationError, ProviderError, ValueError) as error:
        print(f"Setup error: {error}")
        return 1

    print("Chatbot ready. Type 'exit' to quit or 'clear' to forget this chat.")
    while True:
        try:
            user_text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return 0
        command = user_text.strip().lower()
        if command in {"exit", "quit"}:
            print("Goodbye!")
            return 0
        if command == "clear":
            chatbot.clear_history()
            print("Conversation cleared.")
            continue
        try:
            print(f"Assistant: {chatbot.reply(user_text)}")
        except (ValueError, ProviderError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
