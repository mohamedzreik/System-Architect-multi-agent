from typing import Any, Dict, List, Optional
import sys
from app.core.context import Context
from app.core.cache import Cache
from app.agents.requirements_agent import RequirementsAgent
from app.agents.usecase_agent import UseCaseAgent
from app.agents.security_agent import SecurityAgent
from app.agents.apispec_agent import APISpecAgent
from app.agents.dbdesigner_agent import DBDesignerAgent
from app.agents.sysarchitect_agent import SysArchitectAgent
import os

class Orchestrator:
    def __init__(self, vector_store: Any, api_key: Optional[str] = None):
        self.vector_store = vector_store
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.cache = Cache()

        self.security_agent = SecurityAgent(vector_store, self.api_key)
        self.apispec_agent = APISpecAgent(vector_store, self.api_key)

        self.requirements_agent = RequirementsAgent(vector_store, self.api_key)
        self.usecase_agent = UseCaseAgent(vector_store, self.api_key, self.security_agent)
        self.dbdesigner_agent = DBDesignerAgent(vector_store, self.api_key)
        self.sysarchitect_agent = SysArchitectAgent(vector_store, self.api_key, self.apispec_agent)

    def _decide_agents(self, query: str) -> List[str]:
        query_lower = query.lower()
        agents = []
        
        if any(word in query_lower for word in ["requirement", "feature", "functionality", "need"]):
            agents.append("requirements")
        
        if any(word in query_lower for word in ["use case", "usecase", "actor", "flow", "scenario"]):
            agents.append("usecase")
        
        if any(word in query_lower for word in ["security", "threat", "vulnerability", "auth", "permission"]):
            agents.append("security")
        
        if any(word in query_lower for word in ["api", "endpoint", "rest", "graphql", "request", "response"]):
            agents.append("api")
        
        if any(word in query_lower for word in ["database", "schema", "table", "entity", "data model"]):
            agents.append("database")
        
        if any(word in query_lower for word in ["architecture", "system design", "component", "service"]):
            agents.append("architecture")
        
        if not agents:
            agents.append("requirements")
        
        return agents
    
    def process(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        if use_cache and self.cache.has(query):
            return self.cache.get(query)
        
        context = Context(query=query)
        agent_names = self._decide_agents(query)
        
        results = {}
        
        for agent_name in agent_names:
            if agent_name == "requirements":
                result = self.requirements_agent.analyze(query, context)
            elif agent_name == "usecase":
                result = self.usecase_agent.analyze(query, context)
            elif agent_name == "security":
                result = self.security_agent.analyze(query, context)
            elif agent_name == "api":
                result = self.apispec_agent.analyze(query, context)
            elif agent_name == "database":
                result = self.dbdesigner_agent.analyze(query, context)
            elif agent_name == "architecture":
                result = self.sysarchitect_agent.analyze(query, context)
            else:
                continue
            
            results[agent_name] = result
            context.add_agent_result(agent_name, result)
        
        final_response = self._assemble_response(query, results)
        
        if use_cache:
            self.cache.set(query, final_response)
        
        return final_response
    
    def _assemble_response(self, query: str, results: Dict[str, Any]) -> Dict[str, Any]:
        response_parts = []
        all_sources = []
        total_chunks = 0
        
        for agent_name, result in results.items():
            response_parts.append(f"=== {result['agent']} ===")
            response_parts.append(result['response'])
            response_parts.append("")
            all_sources.extend(result.get('sources', []))
            total_chunks += result.get('chunks_used', 0)
        
        combined_response = "\n".join(response_parts)
        unique_sources = list(set(all_sources))
        
        return {
            "query": query,
            "response": combined_response,
            "agents_used": list(results.keys()),
            "total_chunks": total_chunks,
            "sources": unique_sources
        }
