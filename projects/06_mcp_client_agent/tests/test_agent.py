from types import SimpleNamespace

import pytest

from mcp_client_agent.llm_agent import LLMAgent


class FakeMCPClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def call_tool(self, tool_name: str, arguments: dict):
        self.calls.append((tool_name, arguments))

        if tool_name == "search_tickets_tool":
            return {
                "tickets": [
                    {
                        "id": "INC1001",
                        "title": "VM CPU utilization high",
                        "status": "Open",
                        "priority": "High",
                    }
                ],
                "count": 1,
            }

        raise AssertionError(f"Unexpected tool: {tool_name}")


class FakeResponses:
    def __init__(self) -> None:
        self.call_count = 0

    def create(self, **kwargs):
        self.call_count += 1

        # First LLM call requests a tool.
        if self.call_count == 1:
            return SimpleNamespace(
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="search_tickets_tool",
                        arguments=(
                            '{"query":"open high priority tickets",'
                            '"status":"Open",'
                            '"priority":"High",'
                            '"limit":10}'
                        ),
                        call_id="call_001",
                    )
                ],
                output_text="",
            )

        # Second LLM call returns the final answer.
        return SimpleNamespace(
            output=[],
            output_text=(
                "There is 1 open high-priority ticket: INC1001."
            ),
        )


class FakeOpenAI:
    def __init__(self) -> None:
        self.responses = FakeResponses()


@pytest.mark.anyio
async def test_agent_routes_to_allowed_mcp_tool() -> None:
    mcp_client = FakeMCPClient()
    openai_client = FakeOpenAI()

    agent = LLMAgent(
        mcp_client=mcp_client,
        openai_client=openai_client,
        model="test-model",
    )

    response = await agent.run(
        "Find open high priority tickets"
    )

    assert response.tool_name == "search_tickets_tool"

    assert response.tool_arguments == {
        "query": "open high priority tickets",
        "status": "Open",
        "priority": "High",
        "limit": 10,
    }

    assert mcp_client.calls == [
        (
            "search_tickets_tool",
            {
                "query": "open high priority tickets",
                "status": "Open",
                "priority": "High",
                "limit": 10,
            },
        )
    ]

    assert "INC1001" in response.answer


@pytest.mark.anyio
async def test_agent_rejects_disallowed_tool() -> None:
    class BadResponses:
        def create(self, **kwargs):
            return SimpleNamespace(
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="delete_everything",
                        arguments="{}",
                        call_id="bad_001",
                    )
                ],
                output_text="",
            )

    class BadOpenAI:
        def __init__(self) -> None:
            self.responses = BadResponses()

    agent = LLMAgent(
        mcp_client=FakeMCPClient(),
        openai_client=BadOpenAI(),
        model="test-model",
    )

    with pytest.raises(ValueError, match="disallowed tool"):
        await agent.run("Do something dangerous")


def test_agent_requires_model() -> None:
    class FakeClient:
        pass

    with pytest.raises(ValueError, match="OPENAI_MODEL"):
        LLMAgent(
            mcp_client=FakeMCPClient(),
            openai_client=FakeClient(),
            model=None,
        )