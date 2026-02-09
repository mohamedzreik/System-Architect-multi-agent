from typing import Any, Dict, Optional
import sys
from app.core.base_agent import BaseAgent

class UseCaseAgent(BaseAgent):
    def __init__(self, vector_store: Any, llm_client: Any, security_agent: Optional[Any] = None):
        super().__init__(vector_store, llm_client)
        self.security_agent = security_agent
    
    def analyze(self, query: str, context: Any = None) -> Dict[str, Any]:
        filters = {"source_type": "usecase"}
        chunks = self._retrieve_chunks(query, k=5, filters=filters)
        
        context_text = self._format_context(chunks)
        
        security_info = ""
        if self.security_agent and "security" in query.lower():
            security_result = self.security_agent.analyze(query, context)
            security_info = f"\n\nSecurity considerations:\n{security_result['response']}"
        
        prompt = f"""You are a use case analyst. Based on the following information, describe the use cases.

Query: {query}

Context:
{context_text}
{security_info}

Please provide:
1. Use case name and ID
2. Actors involved
3. Main flow of events
4. Alternative flows
5. Preconditions and postconditions

Format your response clearly."""

        response = self._call_llm(prompt)
        
        return {
            "agent": self.agent_name,
            "query": query,
            "response": response,
            "chunks_used": len(chunks),
            "sources": [chunk.metadata.get("filename", "unknown") for chunk, _ in chunks]
        }
