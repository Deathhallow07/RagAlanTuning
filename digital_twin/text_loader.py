from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Tuple

from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return clean_text(path.read_text(encoding="utf-8", errors="ignore"))
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return clean_text("\n".join(parts))
    raise ValueError(f"Unsupported file type: {path}")


def iter_source_files(corpus_dir: Path) -> Iterable[Path]:
    for path in sorted(corpus_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def chunk_words(text: str, chunk_size: int, overlap: int) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        chunk = words[start : start + chunk_size]
        if len(chunk) < 30 and chunks:
            break
        chunks.append(" ".join(chunk))
    return chunks


def make_chunks(corpus_dir: Path, chunk_size: int, overlap: int) -> List[Tuple[str, str, int, str]]:
    rows: List[Tuple[str, str, int, str]] = []
    for path in iter_source_files(corpus_dir):
        text = load_document(path)
        for idx, chunk in enumerate(chunk_words(text, chunk_size, overlap)):
            rel = str(path.relative_to(corpus_dir))
            rows.append((rel, path.stem, idx, chunk))
    return rows
