from typing import Any, Dict, Optional
import sys
from app.core.base_agent import BaseAgent

class SysArchitectAgent(BaseAgent):
    def __init__(self, vector_store: Any, llm_client: Any, apispec_agent: Optional[Any] = None):
        super().__init__(vector_store, llm_client)
        self.apispec_agent = apispec_agent
    
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "architecture"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        api_info = ""
        if self.apispec_agent and "api" in query.lower():
            api_result = self.apispec_agent.analyze(query, context)
            api_info = f"\n\nAPI specifications:\n{api_result['response']}"
        
        prompt = f"""You are a system architect. Based on the following information, provide system architecture recommendations.

Query: {query}

Context:
{context_text}
{api_info}

Please provide:
1. High-level system architecture
2. Component breakdown and responsibilities
3. Communication patterns between components
4. Technology stack recommendations
5. Scalability and performance considerations

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
