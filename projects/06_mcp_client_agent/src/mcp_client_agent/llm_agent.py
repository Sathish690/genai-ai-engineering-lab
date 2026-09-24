from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .mcp_client import MCPClient
from .models import AgentRequest, AgentResponse


ALLOWED_TOOL_NAMES = {
    "search_tickets_tool",
    "get_ticket_tool",
}


TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "search_tickets_tool",
        "description": (
            "Search the local read-only ticket dataset by keyword, "
            "status, and priority."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Optional text to match against ticket ID, "
                        "title, and description."
                    ),
                },
                "status": {
                    "type": ["string", "null"],
                    "enum": ["Open", "In Progress", "Resolved", None],
                    "description": "Optional ticket status filter.",
                },
                "priority": {
                    "type": ["string", "null"],
                    "enum": ["Low", "Medium", "High", None],
                    "description": "Optional ticket priority filter.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 50,
                    "description": "Maximum number of results.",
                },
            },
            "required": [
                "query",
                "status",
                "priority",
                "limit",
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_ticket_tool",
        "description": (
            "Retrieve one ticket from the local read-only dataset "
            "using its ticket ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "string",
                    "description": "Ticket ID such as INC1001.",
                }
            },
            "required": ["ticket_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


SYSTEM_INSTRUCTIONS = """
You are a ticket-support assistant.

You have access only to two explicitly allowed, read-only MCP tools:
- search_tickets_tool
- get_ticket_tool

Use a tool when the user's question requires information from the
ticket dataset.

Never invent ticket information.

If the requested information is not available from the tools,
say that it was not found.

Never request or execute arbitrary tools, URLs, shell commands,
filesystem paths, or write operations.

Keep the final answer concise and explain which tool was used when
appropriate.
""".strip()


class LLMAgent:
    """LLM agent that routes requests to safe MCP read-only tools."""

    def __init__(
        self,
        mcp_client: MCPClient,
        openai_client: OpenAI | None = None,
        model: str | None = None,
    ) -> None:
        self._mcp_client = mcp_client
        self._client = openai_client or OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        configured_model = model or os.getenv("OPENAI_MODEL")

        if not configured_model:
            raise ValueError(
                "OPENAI_MODEL environment variable is required."
            )

        self._model = configured_model

    def _find_function_calls(self, response: Any) -> list[Any]:
        """Return only function-call items from the model response."""
        return [
            item
            for item in response.output
            if getattr(item, "type", None) == "function_call"
        ]

    async def run(self, question: str) -> AgentResponse:
        """Run one user request through the LLM + MCP workflow."""
        request = AgentRequest(question=question)

        input_items: list[Any] = [
            {
                "role": "user",
                "content": request.question,
            }
        ]

        response = self._client.responses.create(
            model=self._model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            input=input_items,
        )

        tool_calls = self._find_function_calls(response)

        if not tool_calls:
            return AgentResponse(
                answer=response.output_text,
            )

        input_items += response.output

        first_tool_name: str | None = None
        first_tool_arguments: dict[str, Any] | None = None

        for tool_call in tool_calls:
            tool_name = tool_call.name

            if tool_name not in ALLOWED_TOOL_NAMES:
                raise ValueError(
                    f"Model requested disallowed tool: {tool_name}"
                )

            arguments = json.loads(tool_call.arguments)

            if first_tool_name is None:
                first_tool_name = tool_name
                first_tool_arguments = arguments

            print(
                f"[DEBUG] MCP tool call: "
                f"{tool_name}({json.dumps(arguments)})"
            )

            tool_result = await self._mcp_client.call_tool(
                tool_name,
                arguments,
            )

            print(
                f"[DEBUG] MCP tool result: "
                f"{json.dumps(tool_result, default=str)}"
            )

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        tool_result,
                        default=str,
                    ),
                }
            )

        final_response = self._client.responses.create(
            model=self._model,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=TOOL_DEFINITIONS,
            input=input_items,
        )

        return AgentResponse(
            answer=final_response.output_text,
            tool_name=first_tool_name,
            tool_arguments=first_tool_arguments,
        )