from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional
from app.data_pipeline.chunking import Chunk
from openai import OpenAI
import os


class BaseAgent(ABC):
    def __init__(self, vector_store: Any, api_key: Optional[str] = None):
        self.vector_store = vector_store
        self.agent_name = self.__class__.__name__

        if api_key:
            self.llm_client = OpenAI(api_key=api_key)
        else:
            self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    @abstractmethod
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        pass

    def _retrieve_chunks(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[
        Tuple[Chunk, float]]:
        return self.vector_store.search(query=query, k=k, filter_metadata=filters)

    def _format_context(self, chunks: List[Tuple[Chunk, float]]) -> str:
        if not chunks:
            return "No relevant information found."

        context_parts = []
        for idx, (chunk, score) in enumerate(chunks):
            context_parts.append(f"[Source {idx + 1}] (relevance: {score:.2f})")
            context_parts.append(chunk.text)
            context_parts.append("")

        return "\n".join(context_parts)

    def _call_llm(self, prompt: str) -> str:
        response = self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content