# GenAI AI Engineering Lab

A practical Generative AI engineering portfolio containing nine small, independently runnable projects covering LLM applications, structured extraction, RAG, hybrid search, MCP, PDF processing, OCR, and multimodal document AI.

The repository focuses on practical AI engineering skills including:

- LLM integration and prompt engineering
- Structured JSON extraction and validation
- Retrieval-Augmented Generation (RAG)
- Hybrid keyword + vector retrieval
- Model Context Protocol (MCP)
- Agent and tool integration
- PDF and document processing
- Image OCR and document classification
- Multimodal document understanding
- Testing, security, configuration, and documentation

---

## Repository Overview

| Project | Topic | Main Goal |
|---|---|---|
| 01 | LLM Chatbot | Build a CLI chatbot with system prompts and conversation history |
| 02 | Structured LLM Extractor | Convert unstructured text into validated JSON |
| 03 | Basic RAG | Retrieve relevant document content and generate source-grounded answers |
| 04 | Hybrid RAG | Combine keyword and semantic retrieval |
| 05 | MCP Server | Expose safe read-only tools and resources through MCP |
| 06 | MCP Client + Agent | Connect an LLM agent to MCP tools |
| 07 | PDF Processor | Extract PDF text and metadata with optional OCR |
| 08 | Image OCR Processor | Process images, extract text, and classify documents |
| 09 | Multimodal Document AI | Compare OCR extraction with vision-based structured extraction |

---

## Project Structure

```text
genai-ai-engineering-lab/
│
├── README.md
├── .gitignore
├── .env.example
│
├── projects/
│   │
│   ├── 01_llm_chatbot/
│   ├── 02_structured_llm_extractor/
│   ├── 03_rag_document_qa/
│   ├── 04_rag_hybrid_search/
│   ├── 05_mcp_server/
│   ├── 06_mcp_client_agent/
│   ├── 07_pdf_processor/
│   ├── 08_image_ocr_processor/
│   └── 09_multimodal_document_ai/
│
├── architecture/
│   └── README.md
│
└── docs/
    └── README.md