from typing import Any, Dict, Optional
import sys
from app.core.base_agent import BaseAgent

class RequirementsAgent(BaseAgent):
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "requirements"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        prompt = f"""You are a requirements analyst. Based on the following information, extract and list the requirements.

Query: {query}

Context:
{context_text}

Please provide:
1. Functional requirements
2. Non-functional requirements
3. Any constraints or dependencies

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
