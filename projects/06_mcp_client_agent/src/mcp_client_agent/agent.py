from __future__ import annotations

import argparse
import asyncio

from .llm_agent import LLMAgent
from .mcp_client import MCPClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MCP Client + LLM Agent"
    )

    parser.add_argument(
        "question",
        nargs="?",
        help="Question to ask the agent.",
    )

    return parser.parse_args()


async def run_agent(question: str) -> None:
    mcp_client = MCPClient()
    agent = LLMAgent(mcp_client)

    response = await agent.run(question)

    print("\n=== Final Answer ===")
    print(response.answer)

    if response.tool_name:
        print("\n=== Tool Used ===")
        print(response.tool_name)

    if response.tool_arguments:
        print("\n=== Tool Arguments ===")
        print(response.tool_arguments)


async def main() -> None:
    args = parse_args()

    if args.question:
        try:
            await run_agent(args.question)
        except Exception as exc:
            print(f"\nError: {exc}\n")
        return

    print("MCP Client + Agent")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        try:
            await run_agent(question)
        except Exception as exc:
            print(f"\nError: {exc}\n")


if __name__ == "__main__":
    asyncio.run(main()) 