# shared/src/magicc_shared/core/command.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .context import Context
from .result import Result


class Command(ABC):
    """命令抽象基类"""
    
    @abstractmethod
    def execute(self, ctx: Context) -> Result:
        """执行命令"""
        pass
    
    def validate(self, ctx: Context) -> None:
        """验证前置条件（可选）"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """返回命令元数据"""
        return {
            "name": self.__class__.__name__,
            "description": "",
            "requires_llm": False,
        }


class LLMCommand(Command):
    """需要 LLM 的命令抽象基类"""
    
    def __init__(self):
        self._llm_client = None
        self._model_name = None
    
    def set_llm_client(self, client, model_name: str) -> None:
        """注入 LLM 客户端"""
        self._llm_client = client
        self._model_name = model_name
    
    def get_llm_client(self):
        """获取 LLM 客户端"""
        return self._llm_client
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self._model_name
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta["requires_llm"] = True
        return meta
    
    @abstractmethod
    def execute(self, ctx: Context) -> Result:
        """执行命令（子类实现）"""
        pass