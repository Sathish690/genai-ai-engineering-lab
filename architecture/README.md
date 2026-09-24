# Architecture Overview

This directory contains the portfolio-level architecture and data-flow documentation for the GenAI AI Engineering Lab.

The repository contains nine independent projects covering LLM applications, RAG, MCP, document processing, OCR, and multimodal AI.

---

## Portfolio Architecture

```mermaid
flowchart TB

    A[User / Application]

    A --> P1[01 LLM Chatbot]
    A --> P2[02 Structured LLM Extractor]
    A --> P3[03 Basic RAG]
    A --> P4[04 Hybrid RAG]
    A --> P5[05 MCP Server]
    A --> P6[06 MCP Client + Agent]
    A --> P7[07 PDF Processor]
    A --> P8[08 Image OCR Processor]
    A --> P9[09 Multimodal Document AI]

    P7 --> P3
    P8 --> P9
    P5 --> P6