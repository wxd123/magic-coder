# magicc_shared/core/context.py

from typing import Any, Dict, Optional

class Context:
    """
    简单的字典包装器，提供键值对数据的上下文管理。
    
    该类封装了字典操作，提供了类型安全的 get/set 方法，
    支持链式调用和数据转换功能。适用于传递共享状态或配置信息。
    
    示例:
        >>> ctx = Context({"user": "admin"})
        >>> ctx.get("user")
        'admin'
        >>> ctx.set("role", "editor").get("role")
        'editor'
        >>> ctx.has("user")
        True
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        初始化上下文对象。
        
        Args:
            data: 初始字典数据，若为 None 则初始化为空字典。
        """
        self._data = data or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取指定键的值。
        
        Args:
            key: 要查询的键名。
            default: 键不存在时返回的默认值，默认为 None。
        
        Returns:
            键对应的值，若键不存在则返回 default。
        """
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> 'Context':
        """
        设置键值对，支持链式调用。
        
        Args:
            key: 要设置的键名。
            value: 要设置的值。
        
        Returns:
            返回当前 Context 实例，便于链式调用。
        
        示例:
            >>> ctx = Context().set("a", 1).set("b", 2)
        """
        self._data[key] = value
        return self
    
    def has(self, key: str) -> bool:
        """
        检查指定键是否存在。
        
        Args:
            key: 要检查的键名。
        
        Returns:
            键存在时返回 True，否则返回 False。
        """
        return key in self._data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将上下文数据转换为字典副本。
        
        Returns:
            包含当前所有键值对的字典副本（浅拷贝）。
        
        注意:
            返回的是副本，修改返回值不会影响原 Context 对象。
        """
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """
        从字典创建 Context 实例。
        
        Args:
            data: 源字典数据。
        
        Returns:
            使用 data 初始化的新 Context 实例。
        
        示例:
            >>> ctx = Context.from_dict({"name": "test"})
        """
        return cls(data)