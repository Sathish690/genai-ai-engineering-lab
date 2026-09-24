# Project 6 — MCP Client + Agent

## Problem

This project demonstrates an LLM-powered application that connects to the read-only MCP server from Project 5.

The LLM decides when to use an MCP tool, the MCP client safely routes the call to the server, and the tool result is returned to the LLM for the final answer.

## Architecture

```mermaid
flowchart TD
    User[User] --> Agent[LLM Agent]
    Agent --> LLM[LLM]
    LLM -->|Tool decision| Client[MCP Client]
    Client --> Server[Project 5 MCP Server]
    Server --> Search[search_tickets_tool]
    Server --> Get[get_ticket_tool]
    Search --> Data[(tickets.json)]
    Get --> Data
    Server --> Client
    Client --> Agent
    Agent --> LLM
    LLM --> Answer[Final Answer]