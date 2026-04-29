# magicc_shared/core/context.py

from typing import Any, Dict, Optional

class Context:
    """简单的字典包装器"""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> 'Context':
        self._data[key] = value
        return self
    
    def has(self, key: str) -> bool:
        return key in self._data
    
    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        return cls(data)