import json

import pytest
from mcp import Client

from mcp_server.server import mcp


def get_tool_data(result):
    """Read tool output from structured content or JSON text content."""
    assert result.is_error is False
    assert result.content, "MCP tool returned no content."

    if result.structured_content is not None:
        data = result.structured_content

        # Some MCP SDK versions wrap structured output as {"result": ...}
        if isinstance(data, dict) and set(data.keys()) == {"result"}:
            return data["result"]

        return data

    text_block = result.content[0]

    if not hasattr(text_block, "text"):
        raise AssertionError("Expected text content from MCP tool.")

    return json.loads(text_block.text)


@pytest.mark.anyio
async def test_server_exposes_required_tools() -> None:
    async with Client(mcp) as client:
        result = await client.list_tools()

    tool_names = {tool.name for tool in result.tools}

    assert "search_tickets_tool" in tool_names
    assert "get_ticket_tool" in tool_names


@pytest.mark.anyio
async def test_search_tickets_by_keyword() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_tickets_tool",
            {"query": "CPU"},
        )

    data = get_tool_data(result)

    # Supports both direct response and TicketSearchResponse.
    if isinstance(data, dict) and "tickets" in data:
        tickets = data["tickets"]
    else:
        tickets = data

    assert isinstance(tickets, list)
    assert len(tickets) >= 1
    assert tickets[0]["id"] == "INC1001"


@pytest.mark.anyio
async def test_search_tickets_by_priority() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_tickets_tool",
            {"priority": "High"},
        )

    data = get_tool_data(result)

    tickets = data["tickets"] if isinstance(data, dict) else data

    assert isinstance(tickets, list)
    assert len(tickets) >= 1
    assert all(
        ticket["priority"] == "High"
        for ticket in tickets
    )


@pytest.mark.anyio
async def test_search_tickets_by_status() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "search_tickets_tool",
            {"status": "Open"},
        )

    data = get_tool_data(result)

    tickets = data["tickets"] if isinstance(data, dict) else data

    assert isinstance(tickets, list)
    assert len(tickets) >= 1
    assert all(
        ticket["status"] == "Open"
        for ticket in tickets
    )


@pytest.mark.anyio
async def test_get_ticket_by_id() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_ticket_tool",
            {"ticket_id": "INC1003"},
        )

    ticket = get_tool_data(result)

    assert isinstance(ticket, dict)
    assert ticket["id"] == "INC1003"
    assert ticket["priority"] == "Medium"


@pytest.mark.anyio
async def test_get_unknown_ticket_returns_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "get_ticket_tool",
            {"ticket_id": "INC9999"},
        )

    assert result.is_error is True


@pytest.mark.anyio
async def test_metadata_resource() -> None:
    async with Client(mcp) as client:
        result = await client.read_resource(
            "server://metadata"
        )

    assert len(result.contents) == 1

    metadata_text = result.contents[0].text
    metadata = json.loads(metadata_text)

    assert metadata["name"] == "Ticket MCP Server"
    assert metadata["version"] == "1.0.0"
    assert metadata["ticket_count"] == 5