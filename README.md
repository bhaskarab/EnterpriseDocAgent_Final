# EnterpriseDocAgent

A Generative AI–powered enterprise document assistant built using RAG (Retrieval-Augmented Generation), LangGraph multi-agent orchestration, and local LLM inference.

**Author:** Bhaskara Reddy B  
**License:** MIT

---

## Overview

EnterpriseDocAgent allows users to upload enterprise documents in multiple formats and ask natural-language questions. The system retrieves relevant content using ChromaDB semantic search and generates accurate, grounded responses with numbered citations using Ollama (local LLM).

Upload your own documents via the **Streamlit sidebar** to get started. No sample data is bundled in this repository — add your PDF, TXT, CSV, Excel, JSON, YAML, or Markdown files through the UI.

---

## Tech Stack

| Component     | Technology                                |
|---------------|-------------------------------------------|
| Language      | Python 3.11+                              |
| Backend       | FastAPI (optional REST API)               |
| LLM           | Ollama (`llama3`) — local, no API key     |
| Orchestration | LangGraph multi-agent workflow            |
| Vector Store  | ChromaDB                                  |
| Embeddings    | Sentence Transformers (all-MiniLM-L6-v2)  |
| UI            | Streamlit                                 |
| Deployment    | Docker Compose                            |

---

## System Architecture

> See the full architecture diagram: [`architecture/EnterpriseDocAgent_Architecture_Diagram.png`](architecture/EnterpriseDocAgent_Architecture_Diagram.png)  
> Editable source: [`architecture/EnterpriseDocAgent_Architecture.drawio`](architecture/EnterpriseDocAgent_Architecture.drawio) (open in [draw.io](https://app.diagrams.net))  
> Text reference: [`architecture/system_diagram.md`](architecture/system_diagram.md)

### Document Ingestion Flow

```text
User uploads document
        ↓
Input Validation (validator.py)
        ↓
DocumentProcessor → IngestionService
        ↓
ChunkingService → EmbeddingService
        ↓
ChromaDB (VectorStoreService)
```

### Query Flow

```text
User Question
        ↓
Streamlit UI (streamlit_app.py)
        ↓
Input Validation (validator.py)
        ↓
LangGraph Agents (router → retriever → synthesizer)
        ↓
RAGService → ChromaDB (Similarity Search)
        ↓
Ollama LLM generates grounded answer
        ↓
CitationService → numbered source references
        ↓
Guardrails (guardrails.py) → Validated Response
        ↓
Streamlit UI displays answer + citations to User
```

---

## Agent Workflow

| Role        | Description                                                |
|-------------|------------------------------------------------------------|
| Router      | Classifies query intent (factual, summary, comparison, listing) |
| Retriever   | Searches ChromaDB for relevant document chunks             |
| Synthesizer | Combines retrieved context with Ollama LLM to generate answer |

---

## Project Structure

```text
EnterpriseDocAgent/
├── app/                        # Application source code
│   ├── agents/                 # LangGraph workflow (graph.py, nodes.py)
│   ├── api/                    # FastAPI endpoints (optional)
│   ├── core/                   # Config and RAG pipeline
│   ├── services/               # Ingestion, embeddings, vector store, RAG
│   └── utils/                  # Validation, guardrails, Ollama health
├── architecture/               # Architecture diagram and documentation
├── data/
│   ├── chroma/                 # ChromaDB index (created at runtime, gitignored)
│   └── uploads/                # Uploaded files (created at runtime, gitignored)
├── deployment/                 # Dockerfiles
├── main.py                     # Config verification entry point
├── demo_llm.py                 # LLM + RAG smoke test
├── ingest_docs.py              # Optional batch ingestion from a local data/ folder
├── streamlit_app.py            # Streamlit UI (primary)
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- [Ollama](https://ollama.com) installed
- Model: `ollama pull llama3`

### Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/EnterpriseDocAgent_Final.git
cd EnterpriseDocAgent_Final
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
```

5. Verify configuration and Ollama:

```bash
python main.py
```

6. Run the application:

```bash
streamlit run streamlit_app.py
```

7. Open http://localhost:8501 and **upload documents** via the sidebar before asking questions.

### Optional: FastAPI REST Layer

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Optional: Batch ingestion

If you place files in a local `data/` folder, run:

```bash
python ingest_docs.py
```

---

## Usage

1. Open the app at http://localhost:8501
2. Expand **System Status** — confirm Ollama LLM is ready
3. Upload documents using the sidebar (PDF, TXT, CSV, Excel, JSON, YAML, Markdown)
4. Type your question in the chat input
5. Review the grounded answer and numbered citations

---

## Example Questions

After uploading your own documents, try questions such as:

- What file formats does this system support?
- Summarize the key policies in my uploaded documents.
- What are the security requirements mentioned in the documents?
- List the main topics covered across all uploaded files.

---

## Input Validation Rules

| Rule                  | Limit                               |
|-----------------------|-------------------------------------|
| Minimum query length  | 3 characters                        |
| Maximum query length  | 500 characters                      |
| Maximum file size     | 10 MB                               |
| Supported file types  | PDF, TXT, CSV, XLSX, JSON, YAML, MD |

---

## Limitations

- You must upload documents before querying — no sample data is included in the repo
- ChromaDB is stored locally under `data/chroma/` (created on first run)
- Response quality depends on the relevance of uploaded documents
- Large documents may take time to ingest on first run (embedding model download)
- Supports English language documents only
- Ollama must be running for LLM-powered answers; extractive fallback used otherwise

---

## Security Considerations

- Store secrets in `.env` — never commit it (see `.gitignore`)
- `.gitignore` excludes `.env`, `data/chroma/`, and `data/uploads/`
- Input validation prevents prompt injection attacks
- File size limits prevent denial-of-service via large uploads
- Documents are processed locally on your machine

---

## Deployment

### Run locally

```bash
streamlit run streamlit_app.py
```

### Docker Compose

```bash
docker compose up --build
```

- API: http://localhost:8000
- UI: http://localhost:8501

---

## Author

**Bhaskara Reddy B**

Developed as a Generative AI capstone project — enterprise document intelligence with RAG, LangGraph agents, and local LLM inference.

Architecture diagram designed by **Bhaskara Reddy B** | June 27, 2026
