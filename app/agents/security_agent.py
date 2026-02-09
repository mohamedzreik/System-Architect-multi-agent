from typing import Any, Dict
import sys
from app.core.base_agent import BaseAgent
class SecurityAgent(BaseAgent):
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "security"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        prompt = f"""You are a security analyst. Based on the following information, identify security concerns.

Query: {query}

Context:
{context_text}

Please provide:
1. Identified threats and vulnerabilities
2. Security requirements
3. Recommended security controls
4. Compliance considerations

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
