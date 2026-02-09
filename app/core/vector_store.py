from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import re
from collections import Counter

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
    VectorParams,
    SearchRequest,
)

from app.data_pipeline.chunking import Chunk


class VectorStore(ABC):
    @abstractmethod
    def index(self, chunks: List[Chunk]) -> None:
        ...

    @abstractmethod
    def search(
            self,
            query: str,
            k: int = 5,
            filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Chunk, float]]:
        ...


class QdrantVectorStore(VectorStore):
    def __init__(
            self,
            embed_fn: Callable[[str], np.ndarray],
            collection_name: str = "requirements_collection",
            host: str = "localhost",
            port: int = 6333,
            vector_dim: int = 384,
            distance: Distance = Distance.COSINE,
            hybrid_alpha: float = 0.7,
    ) -> None:
        self.embed_fn = embed_fn
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.hybrid_alpha = float(hybrid_alpha)

        # Use in-memory client
        self.client = QdrantClient(":memory:")
        self._ensure_collection(distance)

    def _ensure_collection(self, distance: Distance) -> None:
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=distance,
                ),
            )
        except Exception:
            # Collection might already exist, try to create it
            pass

    def index(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return

        points: List[PointStruct] = []

        for idx, chunk in enumerate(chunks):
            vec = self.embed_fn(chunk.text)
            if isinstance(vec, np.ndarray):
                vec_list = vec.tolist()
            else:
                raise TypeError("embed_fn must return a numpy.ndarray")

            payload: Dict[str, Any] = {
                "id": chunk.id,
                "text": chunk.text,
                "metadata": chunk.metadata,
            }

            for key, value in chunk.metadata.items():
                payload[key] = value

            point = PointStruct(
                id=idx,
                vector=vec_list,
                payload=payload,
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def _build_filter(self, filter_metadata: Optional[Dict[str, Any]]) -> Optional[Filter]:
        if not filter_metadata:
            return None

        conditions = []
        for key, value in filter_metadata.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value),
                )
            )

        return Filter(must=conditions)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r"\b\w+\b", text.lower())

    def _lexical_score(self, text: str, query: str) -> float:
        query_tokens = self._tokenize(query)
        text_tokens = self._tokenize(text)

        if not query_tokens or not text_tokens:
            return 0.0

        text_counts = Counter(text_tokens)
        score = 0.0

        for qt in query_tokens:
            score += text_counts.get(qt, 0)

        return float(score)

    @staticmethod
    def _normalize_scores(scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0 if s > 0 else 0.0 for s in scores]
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def search(
            self,
            query: str,
            k: int = 5,
            filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Chunk, float]]:

        q_vec = self.embed_fn(query)
        if isinstance(q_vec, np.ndarray):
            q_vec = q_vec.tolist()
        else:
            raise TypeError("embed_fn must return a numpy.ndarray")

        q_filter = self._build_filter(filter_metadata)

        # Use query_points for in-memory client
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=q_vec,
            limit=k,
            query_filter=q_filter,
        )

        hits = search_result.points
        if not hits:
            return []

        semantic_scores: List[float] = []
        lexical_scores: List[float] = []
        chunks: List[Chunk] = []

        for hit in hits:
            payload = hit.payload or {}
            chunk_id = payload.get("id", "")
            text = payload.get("text", "")
            metadata = payload.get("metadata", {}) or {}

            chunk = Chunk(
                id=chunk_id,
                text=text,
                metadata=metadata,
            )
            chunks.append(chunk)

            semantic_scores.append(float(hit.score))
            lexical_scores.append(self._lexical_score(text=text, query=query))

        semantic_norm = self._normalize_scores(semantic_scores)
        lexical_norm = self._normalize_scores(lexical_scores)

        alpha = self.hybrid_alpha
        hybrid_scores = [alpha * s + (1 - alpha) * l for s, l in zip(semantic_norm, lexical_norm)]

        combined = list(zip(chunks, hybrid_scores))
        combined.sort(key=lambda x: x[1], reverse=True)

        return combined[:k]