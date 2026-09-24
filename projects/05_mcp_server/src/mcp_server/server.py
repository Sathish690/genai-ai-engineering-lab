import json

from mcp.server import MCPServer

from .data import get_ticket, load_tickets, search_tickets
from .models import SearchTicketsInput


# Create the MCP server.
mcp = MCPServer(
    "Ticket MCP Server",
    version="1.0.0",
)

# Load the read-only local dataset once when the server starts.
TICKETS = load_tickets()


@mcp.tool()
def search_tickets_tool(
    query: str = "",
    status: str | None = None,
    priority: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search the local ticket dataset.

    Args:
        query: Search text matched against ticket ID, title, and description.
        status: Optional status filter.
        priority: Optional priority filter.
        limit: Maximum number of results to return.
    """
    request = SearchTicketsInput(
        query=query,
        status=status,
        priority=priority,
        limit=limit,
    )

    results = search_tickets(
        TICKETS,
        query=request.query,
        status=request.status,
        priority=request.priority,
        limit=request.limit,
    )

    return [ticket.model_dump() for ticket in results]


@mcp.tool()
def get_ticket_tool(ticket_id: str) -> dict:
    """
    Retrieve one ticket using its ticket ID.

    Args:
        ticket_id: Ticket ID such as INC1001.
    """
    normalized_id = ticket_id.strip().upper()

    if not normalized_id:
        raise ValueError("ticket_id cannot be empty.")

    ticket = get_ticket(TICKETS, normalized_id)

    if ticket is None:
        raise ValueError(
            f"Ticket '{normalized_id}' was not found."
        )

    return ticket.model_dump()


@mcp.resource(
    "server://metadata",
    name="server_metadata",
    description="Read-only metadata about the Ticket MCP Server.",
    mime_type="application/json",
)
def server_metadata() -> str:
    """Return read-only server metadata."""
    metadata = {
        "name": "Ticket MCP Server",
        "version": "1.0.0",
        "description": "Read-only MCP server over a local ticket dataset.",
        "ticket_count": len(TICKETS),
        "tools": [
            "search_tickets_tool",
            "get_ticket_tool",
        ],
        "resources": [
            "server://metadata",
        ],
    }

    return json.dumps(metadata, indent=2)


if __name__ == "__main__":
    mcp.run()