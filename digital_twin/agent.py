from __future__ import annotations

import json
from typing import List

from .config import settings
from .llm import GeminiClient
from .memory import MemoryStore
from .persona import PERSONA_CARD
from .vector_store import SearchResult, VectorStore


class ScientistTwinAgent:
    def __init__(self, session_id: str = "default") -> None:
        self.session_id = session_id
        self.llm = GeminiClient()
        self.store = VectorStore(settings.vector_db_path)
        self.memory = MemoryStore(settings.memory_db_path)

    def _retrieve(self, question: str) -> List[SearchResult]:
        query_emb = self.llm.embed_one(question)
        return self.store.search(query_emb, top_k=settings.top_k)

    def _format_sources(self, results: List[SearchResult]) -> str:
        if not results:
            return "No retrieved sources available."
        blocks = []
        for i, r in enumerate(results, start=1):
            blocks.append(
                f"[S{i}] {r.source_title} | file={r.source_path} | chunk={r.chunk_index} | score={r.score:.3f}\n{r.text}"
            )
        return "\n\n".join(blocks)

    def _format_history(self) -> str:
        turns = self.memory.recent_turns(self.session_id, limit=10)
        if not turns:
            return "No previous turns in this session."
        return "\n".join(f"{role.upper()}: {content}" for role, content in turns)

    def _format_long_term_memory(self) -> str:
        memories = self.memory.list_long_term_memories(limit=20)
        if not memories:
            return "No long-term memories yet."
        return "\n".join(f"- {m}" for m in memories)

    def _maybe_store_memory(self, user_message: str, assistant_message: str) -> None:
        extractor_prompt = f"""
Extract only durable user-specific memories from this exchange.
Keep memories useful for future conversations, such as the user's project goal,
preferred explanation level, or recurring constraints. Do not store private sensitive data.
Return strict JSON: {{"memories": ["..."]}}. If none, return {{"memories": []}}.

User: {user_message}
Assistant: {assistant_message}
""".strip()
        try:
            raw = self.llm.generate(extractor_prompt)
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = json.loads(raw[start:end]) if start >= 0 and end > start else {"memories": []}
            for mem in data.get("memories", [])[:3]:
                self.memory.add_long_term_memory(str(mem))
        except Exception:
            # Memory extraction should never break the chat loop.
            return

    def answer(self, question: str) -> str:
        results = self._retrieve(question)
        prompt = f"""
{PERSONA_CARD}

Conversation memory within this session:
{self._format_history()}

Long-term memory across sessions:
{self._format_long_term_memory()}

Retrieved source excerpts:
{self._format_sources(results)}

User question:
{question}

Answer as the digital twin. Use source labels [S1], [S2] when grounding in retrieved text.
End with a tiny "Sources used" list containing only the source labels you actually used.
""".strip()
        self.memory.add_turn(self.session_id, "user", question)
        response = self.llm.generate(prompt)
        self.memory.add_turn(self.session_id, "assistant", response)
        self._maybe_store_memory(question, response)
        return response
