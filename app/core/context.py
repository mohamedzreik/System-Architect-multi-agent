from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Context:
    query: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    retrieved_chunks: List[Any] = field(default_factory=list)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})
    
    def add_filter(self, key: str, value: Any) -> None:
        self.metadata_filters[key] = value
    
    def add_agent_result(self, agent_name: str, result: Any) -> None:
        self.agent_results[agent_name] = result
    
    def get_history_text(self) -> str:
        history = []
        for msg in self.conversation_history:
            history.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(history)
