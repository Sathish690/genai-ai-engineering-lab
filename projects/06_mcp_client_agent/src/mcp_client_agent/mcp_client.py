from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters


PROJECT6_ROOT = Path(__file__).resolve().parents[2]
PROJECT5_ROOT = PROJECT6_ROOT.parent / "05_mcp_server"
PROJECT5_SRC = PROJECT5_ROOT / "src"


class MCPClient:
    """Safe client for the read-only Project 5 MCP server."""

    ALLOWED_TOOLS = {
        "search_tickets_tool",
        "get_ticket_tool",
    }

    def __init__(self) -> None:
        if not PROJECT5_ROOT.exists():
            raise FileNotFoundError(
                f"Project 5 was not found: {PROJECT5_ROOT}"
            )

        if not PROJECT5_SRC.exists():
            raise FileNotFoundError(
                f"Project 5 source folder was not found: {PROJECT5_SRC}"
            )

    def _server_parameters(self) -> StdioServerParameters:
        """Build parameters for launching Project 5 safely."""
        return StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            cwd=str(PROJECT5_ROOT),
            env={
                "PYTHONPATH": str(PROJECT5_SRC),
            },
        )

    async def list_tools(self) -> list[str]:
        """Return only explicitly allowed tool names."""
        async with Client(self._server_parameters()) as client:
            result = await client.list_tools()

        return [
            tool.name
            for tool in result.tools
            if tool.name in self.ALLOWED_TOOLS
        ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Call one explicitly allowed read-only MCP tool.

        Arbitrary tool names are rejected.
        """
        if tool_name not in self.ALLOWED_TOOLS:
            raise ValueError(
                f"Tool '{tool_name}' is not allowed."
            )

        async with Client(self._server_parameters()) as client:
            result = await client.call_tool(
                tool_name,
                arguments,
            )

        if result.is_error:
            error_text = "MCP tool execution failed."

            if result.content:
                first_content = result.content[0]

                if hasattr(first_content, "text"):
                    error_text = first_content.text

            raise RuntimeError(error_text)

        if result.structured_content is not None:
            return result.structured_content

        if result.content:
            first_content = result.content[0]

            if hasattr(first_content, "text"):
                return first_content.text

        return None

    async def get_metadata(self) -> str:
        """Read the Project 5 server metadata resource."""
        async with Client(self._server_parameters()) as client:
            result = await client.read_resource(
                "server://metadata"
            )

        if not result.contents:
            raise RuntimeError(
                "The MCP server returned no metadata."
            )

        first_content = result.contents[0]

        if not hasattr(first_content, "text"):
            raise RuntimeError(
                "The metadata resource did not return text."
            )

        return first_content.text