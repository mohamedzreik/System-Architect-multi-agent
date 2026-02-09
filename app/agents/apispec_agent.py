from typing import Any, Dict, Optional
import sys
from app.core.base_agent import BaseAgent

class APISpecAgent(BaseAgent):
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "api"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        prompt = f"""You are an API specification designer. Based on the following information, design the API endpoints.

Query: {query}

Context:
{context_text}

Please provide:
1. List of endpoints (method, path, description)
2. Request parameters for each endpoint
3. Response structure for each endpoint
4. Error handling considerations
5. Security requirements for the API

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
