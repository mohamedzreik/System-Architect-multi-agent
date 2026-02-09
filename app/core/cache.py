import hashlib
from typing import Dict, Optional, Any


class Cache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def _hash_query(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Any]:
        key = self._hash_query(query)
        return self._cache.get(key)
    
    def set(self, query: str, response: Any) -> None:
        key = self._hash_query(query)
        self._cache[key] = response
    
    def clear(self) -> None:
        self._cache.clear()
    
    def has(self, query: str) -> bool:
        key = self._hash_query(query)
        return key in self._cache
