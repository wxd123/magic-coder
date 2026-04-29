# magicc_shared/core/result.py

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Result:
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None, message: str = "success") -> 'Result':
        return cls(success=True, message=message, data=data or {})
    
    @classmethod
    def fail(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'Result':
        return cls(success=False, message=message, data=data or {})