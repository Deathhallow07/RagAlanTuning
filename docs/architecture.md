# Architecture Diagram

```mermaid
flowchart TD
    U[User] --> CLI[Interactive CLI app.py]
    CLI --> Agent[ScientistTwinAgent]

    Agent --> M1[Short-term session memory]
    Agent --> M2[Long-term memory SQLite]
    Agent --> E1[Embed user question]
    E1 --> VS[SQLite vector store]
    VS --> R[Top-k retrieved source chunks]

    M1 --> P[Prompt Builder]
    M2 --> P
    R --> P
    Persona[Alan Turing Persona Card] --> P

    P --> Gemini[Gemini 2.5 Flash]
    Gemini --> A[Grounded answer with source labels]
    A --> CLI

    Corpus[data/corpus PDFs, TXT, MD] --> Loader[Document Loader]
    Loader --> Chunker[Chunker]
    Chunker --> Embeddings[Gemini Embeddings]
    Embeddings --> VS
```

## Component responsibilities

- `app.py`: user-facing interactive loop.
- `digital_twin/agent.py`: central orchestration.
- `digital_twin/ingest.py`: builds the RAG index.
- `digital_twin/vector_store.py`: stores and retrieves embedded chunks.
- `digital_twin/memory.py`: stores session turns and persistent memories.
- `digital_twin/persona.py`: defines the scientist's speaking and reasoning style.
- `digital_twin/llm.py`: wraps Gemini generation and embeddings.
