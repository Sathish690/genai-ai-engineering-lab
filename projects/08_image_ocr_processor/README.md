# Project 08 — Image OCR Processor

A Python image-processing pipeline that validates image input, preprocesses the image for OCR, extracts text using Tesseract, returns structured JSON, and optionally performs simple document classification.

---

## Problem

Important information is often stored in image-based documents such as invoices, receipts, forms, and scanned pages.

An OCR pipeline can convert image content into machine-readable text that can be used by downstream applications.

This project demonstrates a simple document-image pipeline with:

- Image validation
- Image preprocessing
- OCR using Tesseract
- Structured JSON output
- Optional document classification

---

## Architecture

```mermaid
flowchart TD
    A[Input Image] --> B[Validate Image]
    B --> C[Preprocess Image]
    C --> D[Tesseract OCR]
    D --> E[Structured JSON]
    E --> F[Optional Classification]