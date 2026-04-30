# magicc_shared/core/result.py

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Result:
    """
    统一的操作结果封装类，用于表示操作的成功/失败状态及相关信息。
    
    该类提供了标准化的结果返回格式，包含成功标志、消息、数据和警告信息。
    通过类方法 ok() 和 fail() 可以方便地创建成功或失败的结果对象。
    
    属性:
        success: 操作是否成功的布尔标志。
        message: 结果消息（成功时为 "success"，失败时为错误描述）。
        data: 附加的数据字典，用于携带额外信息。
        warnings: 警告信息列表，用于记录非致命问题。
    
    示例:
        >>> # 成功结果
        >>> result = Result.ok({"id": 123}, "用户创建成功")
        >>> result.success
        True
        >>> result.data["id"]
        123
        
        >>> # 失败结果
        >>> result = Result.fail("用户不存在", {"user_id": 456})
        >>> result.success
        False
        >>> result.message
        '用户不存在'
        
        >>> # 带警告的结果
        >>> result = Result.ok({"count": 10}, warnings=["部分数据已过滤"])
        >>> result.warnings
        ['部分数据已过滤']
    """
    
    success: bool
    """操作是否成功"""
    
    message: str = ""
    """结果描述信息"""
    
    data: Dict[str, Any] = field(default_factory=dict)
    """附加数据字典，默认为空字典"""
    
    warnings: List[str] = field(default_factory=list)
    """警告信息列表，默认为空列表"""
    
    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None, message: str = "success") -> 'Result':
        """
        创建一个成功的结果对象。
        
        Args:
            data: 附加数据字典，若为 None 则使用空字典。默认为 None。
            message: 成功消息，默认为 "success"。
        
        Returns:
            成功状态的结果对象。
        
        示例:
            >>> result = Result.ok({"status": "completed"})
            >>> result = Result.ok(message="操作完成")
        """
        return cls(success=True, message=message, data=data or {})
    
    @classmethod
    def fail(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'Result':
        """
        创建一个失败的结果对象。
        
        Args:
            message: 失败原因描述（必填）。
            data: 附加数据字典，若为 None 则使用空字典。默认为 None。
        
        Returns:
            失败状态的结果对象。
        
        示例:
            >>> result = Result.fail("数据库连接失败")
            >>> result = Result.fail("权限不足", {"user": "guest", "required": "admin"})
        """
        return cls(success=False, message=message, data=data or {})