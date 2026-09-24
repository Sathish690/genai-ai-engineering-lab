import json
from pathlib import Path

from .models import Ticket


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TICKETS_FILE = PROJECT_ROOT / "data" / "tickets.json"


def load_tickets() -> list[Ticket]:
    """Load and validate the read-only ticket dataset."""
    with TICKETS_FILE.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError("tickets.json must contain a JSON array.")

    return [Ticket.model_validate(item) for item in raw_data]


def search_tickets(
    tickets: list[Ticket],
    query: str = "",
    status: str | None = None,
    priority: str | None = None,
    limit: int = 10,
) -> list[Ticket]:
    """Search tickets using safe in-memory filtering."""
    normalized_query = query.strip().lower()

    results: list[Ticket] = []

    for ticket in tickets:
        if status and ticket.status != status:
            continue

        if priority and ticket.priority != priority:
            continue

        searchable_text = (
            f"{ticket.id} {ticket.title} {ticket.description}"
        ).lower()

        if normalized_query and normalized_query not in searchable_text:
            continue

        results.append(ticket)

        if len(results) >= limit:
            break

    return results


def get_ticket(
    tickets: list[Ticket],
    ticket_id: str,
) -> Ticket | None:
    """Return one ticket by exact ID."""
    normalized_id = ticket_id.strip().upper()

    for ticket in tickets:
        if ticket.id.upper() == normalized_id:
            return ticket

    return None