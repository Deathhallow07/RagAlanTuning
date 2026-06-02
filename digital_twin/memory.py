from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple


class MemoryStore:
    """Session memory + persistent long-term memory in SQLite."""

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
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
                """
            )
            con.commit()

    def now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_turn(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as con:
            con.execute(
                "INSERT INTO turns(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, self.now()),
            )
            con.commit()

    def recent_turns(self, session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT role, content FROM turns
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        return list(reversed([(r[0], r[1]) for r in rows]))

    def add_long_term_memory(self, memory: str) -> None:
        memory = memory.strip()
        if not memory:
            return
        with self._connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO long_term_memory(memory, created_at) VALUES (?, ?)",
                (memory, self.now()),
            )
            con.commit()

    def list_long_term_memories(self, limit: int = 25) -> List[str]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT memory FROM long_term_memory ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [r[0] for r in rows]

    def clear_session(self, session_id: str) -> None:
        with self._connect() as con:
            con.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            con.commit()
