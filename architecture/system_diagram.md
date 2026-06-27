# System Architecture

> **Visual diagram:** [`EnterpriseDocAgent_Architecture_Diagram.png`](EnterpriseDocAgent_Architecture_Diagram.png)  
> **Editable source:** [`EnterpriseDocAgent_Architecture.drawio`](EnterpriseDocAgent_Architecture.drawio) (open in [draw.io](https://app.diagrams.net))

---

## High-Level Diagram

```mermaid
flowchart TB
    subgraph UI["UI Layer"]
        ST[Streamlit UI<br/>streamlit_app.py]
        CHAT[Chat Interface | Session History]
        UPLOAD[Document Upload]
        INGEST_SCRIPT[Batch Ingestion<br/>ingest_docs.py]
    end

    subgraph VAL["Validation Layer"]
        VQ[Query Validation<br/>validator.py]
        VF[File Validation<br/>validator.py — 10MB limit]
    end

    subgraph ING["Data Ingestion Path"]
        DP[Document Processor<br/>document_processor.py]
        CS[Chunking Service<br/>chunking_service.py]
        ES[Embedding Service<br/>all-MiniLM-L6-v2]
    end

    subgraph AGENT["AI Agent Layer — LangGraph"]
        GRAPH[graph.py]
        ROUTER[Router — nodes.py]
        RET[Retriever — nodes.py]
        SYN[Synthesizer — nodes.py]
        RAG[RAG Service<br/>rag_service.py]
        OLLAMA[Ollama LLM<br/>llama3]
        CITE[Citation Service<br/>citation_service.py]
    end

    subgraph OUT["Output Layer"]
        GR[Guardrails<br/>guardrails.py]
    end

    subgraph STORE["Storage"]
        CHROMA[(ChromaDB<br/>data/chroma/)]
        FILES[(Upload Storage<br/>data/uploads/)]
    end

    USER([User]) --> ST
    ST --> CHAT
    ST --> UPLOAD
    INGEST_SCRIPT --> DP

    CHAT --> VQ
    UPLOAD --> VF
    VF --> DP
    VQ --> GRAPH

    DP --> CS --> ES --> CHROMA
    UPLOAD --> FILES

    GRAPH --> ROUTER --> RET --> SYN
    RET --> CHROMA
    SYN --> RAG
    RAG --> OLLAMA
    RAG --> CHROMA
    SYN --> CITE
    SYN --> GR
    GR --> ST
```

---

## Query Path (Primary — Streamlit)

1. User submits a question in **Streamlit** (`streamlit_app.py`)
2. **Query validation** — `validator.py` (length, injection detection)
3. **LangGraph workflow** (`graph.py`):
   - **Router** — classifies intent (factual, summary, comparison, listing)
   - **Retriever** — `vector_store_service.py` similarity search (top-k=5)
   - **Synthesizer** — `rag_service.py` generates answer via **Ollama llama3** (or extractive fallback)
4. **Citation service** — numbered source references
5. **Guardrails** — `guardrails.py` (empty check, grounding, formatting)
6. Streamlit displays answer + citations

---

## Data Ingestion Path

### Option A — Streamlit sidebar upload

1. User uploads file in Streamlit sidebar
2. **File validation** — `validator.py` (10 MB, supported formats)
3. **Document processor** — extract text (PDF, TXT, CSV, XLSX, JSON, YAML, MD)
4. **Chunking** — size 500, overlap 50 (`chunking_service.py`)
5. **Embeddings** — Sentence Transformers `all-MiniLM-L6-v2` (`embedding_service.py`)
6. Chunks stored in **ChromaDB** via `vector_store_service.py`

### Option B — Batch preload

1. Run `python ingest_docs.py`
2. Reads trusted files from `data/` folder
3. Same pipeline: processor → chunking → embeddings → ChromaDB

---

## Optional — FastAPI REST Layer

```text
streamlit_app.py  (primary entry point)
app/api/health.py | upload.py | ask.py  (optional REST API)
docker-compose.yml  (Docker deployment)
```

The Streamlit UI calls `run_agent()` directly. FastAPI endpoints provide an alternate REST interface for the same pipeline services.

---

## Component Responsibilities

| Layer | Components | Role |
|-------|------------|------|
| UI | `streamlit_app.py` | Upload files, chat, display citations |
| Validation | `app/utils/validator.py` | Query and file input checks |
| Ingestion | `document_processor.py`, `ingestion_service.py`, `chunking_service.py`, `embedding_service.py` | Multi-format text extraction, chunking, embedding |
| Agents | `app/agents/graph.py`, `nodes.py`, `state.py` | LangGraph Router → Retriever → Synthesizer |
| RAG | `rag_service.py`, `citation_service.py` | Answer synthesis and source references |
| LLM | Ollama `llama3` (local) | Grounded answer generation |
| Safety | `app/utils/guardrails.py` | Output validation and formatting |
| Storage | `data/chroma/`, `data/uploads/` | Vector index and uploaded files |
| API (optional) | `app/api/*` | REST endpoints for health, upload, ask |
| Reference RAG | `app/core/rag_pipeline.py` | Standalone pipeline (Capstone Guideline 7) |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| UI | Streamlit |
| Orchestration | LangGraph multi-agent workflow |
| LLM | Ollama (`llama3`) — local, no API key |
| Vector Store | ChromaDB |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Backend (optional) | FastAPI |
| Testing | pytest |
| Deployment | Docker Compose |
