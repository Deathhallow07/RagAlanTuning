from __future__ import annotations

import os
from typing import Iterable, List

import numpy as np
from google import genai

from .config import settings


class GeminiClient:
    """Thin wrapper around Google's official GenAI SDK."""

    def __init__(self) -> None:
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Create a .env file or export GEMINI_API_KEY."
            )
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, temperature: float = 0.35) -> str:
        # The SDK supports config objects, but this simple form stays robust across versions.
        response = self.client.models.generate_content(
            model=settings.generation_model,
            contents=prompt,
        )
        return getattr(response, "text", "") or str(response)

    def embed_one(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=settings.embedding_model,
            contents=text,
        )
        # SDK versions expose embeddings slightly differently. Handle common shapes.
        if hasattr(result, "embeddings") and result.embeddings:
            emb = result.embeddings[0]
            if hasattr(emb, "values"):
                return list(emb.values)
            if isinstance(emb, dict) and "values" in emb:
                return list(emb["values"])
        if hasattr(result, "embedding"):
            emb = result.embedding
            if hasattr(emb, "values"):
                return list(emb.values)
            if isinstance(emb, dict) and "values" in emb:
                return list(emb["values"])
        raise RuntimeError(f"Could not parse embedding response: {result}")

    def embed_many(self, texts: Iterable[str]) -> List[List[float]]:
        return [self.embed_one(t) for t in texts]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    va = np.asarray(a, dtype=np.float32)
    vb = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    return float(np.dot(va, vb) / denom)
