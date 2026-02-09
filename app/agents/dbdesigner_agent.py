from typing import Any, Dict
import sys
from app.core.base_agent import BaseAgent

class DBDesignerAgent(BaseAgent):
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "database"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        prompt = f"""You are a database design expert. Based on the following information, provide database design recommendations.

Query: {query}

Context:
{context_text}

Please provide:
1. Proposed database schema (tables and columns)
2. Relationships between entities
3. Indexes and constraints
4. Data types and validations
5. Normalization considerations

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
