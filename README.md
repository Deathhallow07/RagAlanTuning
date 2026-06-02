# Digital Twin of a Scientist - Alan Turing

This repository implements a **Digital Twin of Alan Turing** for the AIMS DTU Summer Project 2026. It uses:

- **Gemini 2.5 Flash** for response generation.
- **Gemini embeddings** for retrieval.
- A local **SQLite vector store** for RAG.
- A local **SQLite memory store** for short-term session memory and persistent long-term memory.
- A persona prompt that keeps the twin mathematically precise, careful, and Turing-like.

The assignment asks for a scientist-specific AI agent with RAG, memory, persona consistency, advanced domain accuracy, and multi-turn conversation support.

## 1. Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_api_key_here
SCIENTIST_NAME=Alan Turing
```

## 2. Add sources

Place Alan Turing source material in:

```text
data/corpus/
```

Supported file types:

- `.txt`
- `.md`
- `.pdf`

The included `alan_turing_starter_notes.md` is only a small demo corpus. For a stronger submission, add primary or high-quality sources such as:

- Turing, *On Computable Numbers, with an Application to the Entscheidungsproblem*.
- Turing, *Computing Machinery and Intelligence*.
- Turing, *The Chemical Basis of Morphogenesis*.
- Lecture notes, interviews, biographies, and public archive material.

## 3. Build the RAG index

```bash
python scripts/ingest_corpus.py
```

This chunks the corpus, embeds each chunk, and stores it in `data/db/vector_store.sqlite3`.

## 4. Run the interactive demo

```bash
python app.py
```

Or resume a previous session:

```bash
python app.py --session demo1
```

Using the same session id keeps the short-term conversation history. Long-term memories persist across sessions in `data/db/memory.sqlite3`.

## 5. Architecture

```text
User question
    |
    v
CLI app.py
    |
    v
ScientistTwinAgent
    |----------------------------|
    |                            |
    v                            v
MemoryStore                 RAG Retriever
short-term turns            query embedding
long-term memory            cosine search over SQLite chunks
    |                            |
    |------------ context --------|
                 |
                 v
Persona Prompt + Retrieved Sources + Memory
                 |
                 v
Gemini 2.5 Flash
                 |
                 v
Grounded answer with source labels [S1], [S2]
```

## 6. Design decisions

### Why Alan Turing?

Turing is a good target because his public work spans computability, AI, cryptanalysis, early computing, and mathematical biology. That makes it possible to test both factual depth and reasoning style.

### Why local SQLite instead of a hosted vector database?

The assignment needs reproducible code. SQLite is simple, portable, and easy to inspect. It avoids requiring Pinecone, Weaviate, or other hosted services.

### Memory design

The project has two memory layers:

1. **Short-term memory**: recent turns from the current session.
2. **Long-term memory**: durable facts extracted from conversations and stored in SQLite.

### RAG design

The ingestion pipeline:

1. Loads `.txt`, `.md`, and `.pdf` files.
2. Cleans and chunks the text.
3. Embeds chunks using Gemini embeddings.
4. Stores chunk text, metadata, and embeddings in SQLite.
5. Retrieves the most relevant chunks using cosine similarity.

### Persona design

The persona card instructs the model to:

- Speak as an educational Alan Turing simulation.
- Use precise mathematical explanations.
- Prefer examples, definitions, and thought experiments.
- Cite retrieved sources.
- Admit uncertainty when sources are insufficient.

## 7. Evaluation checklist

- [x] Gemini 2.5 Flash used for generation.
- [x] RAG pipeline over scientist-specific sources.
- [x] Conversation memory within a session.
- [x] Persistent long-term memory across sessions.
- [x] Persona consistency prompt.
- [x] Interactive demo.
- [x] Architecture diagram.
- [x] Sample conversations.

## 8. Common issues

### `GEMINI_API_KEY is missing`

Create a `.env` file or export the variable manually:

```bash
export GEMINI_API_KEY="your_key"
```

On Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="your_key"
```

### No sources retrieved

Run ingestion again:

```bash
python scripts/ingest_corpus.py
```

Also check that your files are inside `data/corpus/`.
