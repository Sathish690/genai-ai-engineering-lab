# Project 8 — Image OCR + Classification

## Problem

This project processes images by validating the input, preprocessing the image for OCR, extracting text with Tesseract, returning structured JSON, and optionally classifying the document.

## Architecture

```mermaid
flowchart TD
    A[Input Image] --> B[Validate Image]
    B --> C[Preprocess]
    C --> D[Tesseract OCR]
    D --> E[Structured JSON]
    E --> F[Optional Classification]