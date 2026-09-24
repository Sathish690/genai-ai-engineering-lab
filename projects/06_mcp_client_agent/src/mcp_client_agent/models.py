from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


class AgentResponse(BaseModel):
    answer: str
    tool_name: str | None = None
    tool_arguments: dict | None = None