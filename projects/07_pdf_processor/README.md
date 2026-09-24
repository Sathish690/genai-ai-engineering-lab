# Project 07 — PDF / Document Processor

A Python document-processing pipeline that extracts text and metadata from PDF files and produces a normalized JSON representation.

The project supports normal text-based PDFs and provides an optional OCR path for scanned PDFs.

---

## Problem

PDF documents can contain either an extractable text layer or scanned image content.

A document-processing application should first determine whether text can be extracted directly. For scanned documents, OCR can be used as an alternative extraction path.

This project demonstrates both approaches while preserving page-level information and document metadata.

---

## Architecture

```mermaid
flowchart TD
    A[PDF Input] --> B[PDF Validation]
    B --> C[Text Layer Detection]
    C -->|Text Available| D[Page-by-Page Text Extraction]
    C -->|No Text Layer| E[Optional OCR]
    D --> F[Text Normalization]
    E --> F
    F --> G[Page Metadata]
    G --> H[Normalized JSON Output]