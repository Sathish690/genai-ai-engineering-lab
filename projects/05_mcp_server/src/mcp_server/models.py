from typing import Literal

from pydantic import BaseModel, Field


TicketStatus = Literal["Open", "In Progress", "Resolved"]
TicketPriority = Literal["Low", "Medium", "High"]


class Ticket(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    status: TicketStatus
    priority: TicketPriority


class SearchTicketsInput(BaseModel):
    query: str = Field(default="", max_length=200)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    limit: int = Field(default=10, ge=1, le=50)


class TicketSearchResponse(BaseModel):
    tickets: list[Ticket]
    count: int