# Project 9 — Multimodal Document AI

## Problem

This project demonstrates multimodal document understanding by combining:

1. OCR extraction
2. Multimodal vision-based extraction
3. Structured field comparison

The system identifies where OCR and multimodal extraction agree or disagree.

## Architecture

```mermaid
flowchart TD
    A[Document Image] --> B[Input Validation]

    B --> C[OCR Adapter]
    B --> D[Multimodal Vision Extractor]

    C --> E[OCR Structured JSON]
    D --> F[Vision Structured JSON]

    E --> G[Comparator]
    F --> G

    G --> H[Agreement / Disagreement Report]
    H --> I[Final Structured JSON]