# Project 05 — MCP Server

A small Python Model Context Protocol (MCP) server that exposes safe, read-only operations over a local sample ticket dataset.

## Problem

Applications using LLMs may need access to structured external data. MCP provides a standard way for an AI client to discover and call tools exposed by a server.

This project demonstrates an MCP server that provides:

- Ticket search
- Ticket lookup by ID
- Read-only server metadata

The implementation uses a small local JSON dataset and does not expose arbitrary filesystem or shell execution.

---

## Architecture

```mermaid
flowchart TD
    A[MCP Client / Test Harness] --> B[MCP Server]
    B --> C[search_tickets_tool]
    B --> D[get_ticket_tool]
    B --> E[Server Metadata Resource]
    C --> F[Local Ticket Dataset]
    D --> F