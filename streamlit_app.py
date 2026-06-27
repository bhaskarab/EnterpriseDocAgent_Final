import os

import streamlit as st
from loguru import logger

from app.agents.graph import run_agent
from app.core.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.pipeline_service import get_pipeline
from app.utils.guardrails import GuardrailsService
from app.utils.ollama_health import check_ollama_status
from app.utils.validator import InputValidator

st.set_page_config(page_title="EnterpriseDocAgent", page_icon="📄", layout="wide")


@st.cache_resource
def load_pipeline():
    return get_pipeline()


if "validator" not in st.session_state:
    st.session_state.validator = InputValidator()
    st.session_state.guardrails = GuardrailsService()
    st.session_state.processor = DocumentProcessor()
    st.session_state.pipeline = load_pipeline()
    st.session_state.chat_history = []
    st.session_state.uploaded_files = []

st.title("EnterpriseDocAgent")
st.caption(f"Enterprise Document Intelligence | Version {settings.app_version}")

with st.expander("System Status"):
    st.success("Application is running")
    st.info(f"Embedding model: {settings.embedding_model}")
    st.info(f"App version: {settings.app_version}")
    st.info("Vector store: ChromaDB")
    st.info(f"Indexed chunks: {st.session_state.pipeline.vector_store.document_count()}")

    ollama = check_ollama_status()
    if ollama["reachable"] and ollama["model_available"]:
        st.success(f"Ollama LLM ready: {settings.ollama_model} @ {settings.ollama_base_url}")
    elif ollama["reachable"]:
        st.warning(f"Ollama running but model '{settings.ollama_model}' not found. Run: ollama pull {settings.ollama_model}")
    else:
        st.warning("Ollama offline — extractive fallback answers will be used")

with st.sidebar:
    st.header("Document Upload")
    st.caption("Upload documents to query against")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "csv", "xlsx", "json", "yaml", "yml", "md"],
        help="Supported: PDF, TXT, CSV, Excel, JSON, YAML, Markdown. Max size: 10MB",
    )

    if uploaded_file is not None and uploaded_file.name not in st.session_state.uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            try:
                content = uploaded_file.getvalue()
                validation = st.session_state.validator.validate_file_bytes(uploaded_file.name, content)
                if not validation.is_valid:
                    st.error(validation.error_message)
                else:
                    result = st.session_state.pipeline.process_upload(uploaded_file.name, content)
                    st.session_state.uploaded_files.append(uploaded_file.name)
                    st.success(
                        f"{uploaded_file.name} ingested successfully "
                        f"({result['chunks_indexed']} chunks)"
                    )
                    logger.info("File uploaded and ingested: {}", uploaded_file.name)
            except Exception as exc:
                st.error(f"Error processing file: {exc}")
                logger.error("Upload error: {}", exc)

    if st.session_state.uploaded_files:
        st.divider()
        st.subheader("Ingested Documents")
        for fname in st.session_state.uploaded_files:
            st.markdown(f"- {fname}")

    st.divider()
    st.caption("Upload documents via the file picker above, or run `python ingest_docs.py` for batch ingestion from a local folder.")

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

st.subheader("Ask a Question")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything about your enterprise documents..."):
    query_validation = st.session_state.validator.validate_query(prompt)
    if not query_validation.is_valid:
        st.warning(query_validation.error_message)
    elif st.session_state.pipeline.vector_store.document_count() == 0:
        st.warning("No documents indexed yet. Upload files via the sidebar first.")
    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Running multi-agent RAG pipeline..."):
                result = run_agent(prompt, vector_store=st.session_state.pipeline.vector_store)

            validated = st.session_state.guardrails.validate_response(result.get("answer", ""), prompt)
            formatted_answer = st.session_state.guardrails.format_response(validated)

            citations = result.get("citations", [])
            if citations:
                citation_lines = "\n".join(
                    f"- {c['reference']}: {c['excerpt']}" for c in citations
                )
                formatted_answer = f"{formatted_answer}\n\n**Citations**\n{citation_lines}"

            st.markdown(formatted_answer)
            st.caption(
                f"Query type: {result.get('query_type', 'factual')} | "
                f"Context chunks: {result.get('context_used', 0)} | "
                f"LLM used: {result.get('llm_used', False)}"
            )
            st.session_state.chat_history.append({"role": "assistant", "content": formatted_answer})
