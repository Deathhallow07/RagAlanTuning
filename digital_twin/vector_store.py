from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .llm import cosine_similarity


@dataclass
class SearchResult:
    source_path: str
    source_title: str
    chunk_index: int
    text: str
    score: float


class VectorStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    UNIQUE(source_path, chunk_index)
                )
                """
            )
            con.commit()

    def clear(self) -> None:
        with self._connect() as con:
            con.execute("DELETE FROM chunks")
            con.commit()

    def add_chunk(self, source_path: str, source_title: str, chunk_index: int, text: str, embedding: List[float]) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO chunks
                (source_path, source_title, chunk_index, text, embedding_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source_path, source_title, chunk_index, text, json.dumps(embedding)),
            )
            con.commit()

    def count(self) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) FROM chunks").fetchone()
            return int(row[0])

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT source_path, source_title, chunk_index, text, embedding_json FROM chunks"
            ).fetchall()
        scored = []
        for source_path, source_title, chunk_index, text, emb_json in rows:
            emb = json.loads(emb_json)
            scored.append(
                SearchResult(
                    source_path=source_path,
                    source_title=source_title,
                    chunk_index=int(chunk_index),
                    text=text,
                    score=cosine_similarity(query_embedding, emb),
                )
            )
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
