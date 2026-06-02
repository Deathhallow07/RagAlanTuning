from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
DB_DIR = DATA_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    scientist_name: str = os.getenv("SCIENTIST_NAME", "Alan Turing")
    generation_model: str = os.getenv("GENERATION_MODEL", "gemini-2.5-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    vector_db_path: Path = DB_DIR / "vector_store.sqlite3"
    memory_db_path: Path = DB_DIR / "memory.sqlite3"
    chunk_size_words: int = int(os.getenv("CHUNK_SIZE_WORDS", "260"))
    chunk_overlap_words: int = int(os.getenv("CHUNK_OVERLAP_WORDS", "55"))
    top_k: int = int(os.getenv("TOP_K", "5"))


settings = Settings()
