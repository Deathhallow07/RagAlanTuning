from __future__ import annotations

from rich.console import Console
from rich.progress import track

from .config import CORPUS_DIR, settings
from .llm import GeminiClient
from .text_loader import make_chunks
from .vector_store import VectorStore

console = Console()


def ingest(reset: bool = True) -> None:
    console.print(f"[bold]Reading corpus:[/bold] {CORPUS_DIR}")
    chunks = make_chunks(CORPUS_DIR, settings.chunk_size_words, settings.chunk_overlap_words)
    if not chunks:
        console.print("[red]No .txt, .md, or .pdf files found in data/corpus.[/red]")
        return

    store = VectorStore(settings.vector_db_path)
    if reset:
        store.clear()

    llm = GeminiClient()
    for source_path, source_title, chunk_index, text in track(chunks, description="Embedding chunks"):
        emb = llm.embed_one(text)
        store.add_chunk(source_path, source_title, chunk_index, text, emb)

    console.print(f"[green]Done.[/green] Indexed {store.count()} chunks.")


if __name__ == "__main__":
    ingest()
