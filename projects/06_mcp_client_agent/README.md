# Project 06 — MCP Client + Agent

A small Python application that connects an LLM-based agent to the MCP server created in Project 05.

The agent can decide when to use the available read-only MCP tools to retrieve information from a local ticket dataset.

---

## Problem

An LLM may need access to external tools or structured data to answer questions.

This project demonstrates an agent architecture where:

1. The user provides a request.
2. The LLM determines whether a tool is needed.
3. The MCP client connects to the MCP server.
4. The selected read-only tool is invoked.
5. The tool result is returned to the agent.
6. The agent produces a final response.

The MCP server remains responsible for the actual controlled data access.

---

## Architecture

```mermaid
flowchart TD
    A[User] --> B[LLM Agent]
    B --> C{Tool Required?}
    C -->|No| D[Final Response]
    C -->|Yes| E[MCP Client]
    E --> F[MCP Server - Project 05]
    F --> G[Allowed Read-Only Tool]
    G --> H[Local Ticket Dataset]
    H --> G
    G --> F
    F --> E
    E --> B
    B --> D