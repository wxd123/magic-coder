# magicc_shared/core/command.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .context import Context
from .result import Result


class Command(ABC):
    """
    命令抽象基类，定义了命令模式的标准接口。
    
    所有具体命令都应继承此类并实现 execute 方法。可以可选地重写
    validate 方法进行前置条件验证，以及 get_metadata 方法提供元数据。
    
    示例:
        class MyCommand(Command):
            def execute(self, ctx: Context) -> Result:
                value = ctx.get("input")
                # 执行命令逻辑
                return Result.ok({"output": processed_value})
            
            def validate(self, ctx: Context) -> None:
                if not ctx.has("input"):
                    raise ValueError("缺少必需的 'input' 参数")
    """
    
    @abstractmethod
    def execute(self, ctx: Context) -> Result:
        """
        执行命令的核心方法。
        
        Args:
            ctx: 上下文对象，包含命令执行所需的输入数据。
        
        Returns:
            Result 对象，包含执行结果、状态信息和输出数据。
        
        Raises:
            子类可根据需要抛出特定异常。
        """
        pass
    
    def validate(self, ctx: Context) -> None:
        """
        验证命令执行的前置条件（可选重写）。
        
        该方法在 execute 之前调用，用于检查上下文数据是否满足
        命令执行的要求。验证失败时应抛出异常。
        
        Args:
            ctx: 要验证的上下文对象。
        
        Raises:
            验证失败时抛出异常（如 ValueError、KeyError 等）。
        
        示例:
            def validate(self, ctx: Context) -> None:
                if not ctx.has("file_path"):
                    raise ValueError("缺少 file_path 参数")
                if not ctx.get("recursive", False):
                    raise ValueError("需要递归模式")
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        返回命令的元数据信息。
        
        Returns:
            包含命令元数据的字典，默认包含：
                - name: 命令类名
                - description: 描述信息（空字符串）
                - requires_llm: 是否需要 LLM（False）
        
        子类可以重写此方法以添加更多元数据或修改现有值。
        
        示例:
            def get_metadata(self) -> Dict[str, Any]:
                meta = super().get_metadata()
                meta["description"] = "执行文件分析"
                meta["version"] = "1.0"
                return meta
        """
        return {
            "name": self.__class__.__name__,
            "description": "",
            "requires_llm": False,
        }


class LLMCommand(Command):
    """
    需要 LLM（大语言模型）支持的命令抽象基类。
    
    继承自 Command，提供了 LLM 管理器的注入和使用接口。
    子类可以通过 generate 方法调用 LLM 生成响应。
    
    属性:
        _llm_manager: LLM 管理器实例（内部使用）
        _model_name: 模型名称（内部使用）
    
    示例:
        class SummarizeCommand(LLMCommand):
            def execute(self, ctx: Context) -> Result:
                text = ctx.get("text")
                prompt = f"请总结以下文本：\\n{text}"
                summary = self.generate(prompt)
                return Result.ok({"summary": summary})
    """
    
    def __init__(self):
        """初始化 LLM 命令，默认 LLM 管理器为 None。"""
        self._llm_manager = None
        self._model_name = None
    
    def set_llm_manager(self, manager, model_name: str) -> None:
        """
        注入 LLM 管理器。
        
        Args:
            manager: LLM 管理器实例，需实现 generate 方法。
            model_name: 要使用的模型名称。
        
        示例:
            command.set_llm_manager(llm_manager, "gpt-4")
        """
        self._llm_manager = manager
        self._model_name = model_name
    
    def get_llm_manager(self):
        """
        获取 LLM 管理器实例。
        
        Returns:
            当前存储的 LLM 管理器实例，若未设置则为 None。
        """
        return self._llm_manager
    
    def get_model_name(self) -> str:
        """
        获取当前配置的模型名称。
        
        Returns:
            模型名称字符串，若未设置可能为 None。
        """
        return self._model_name
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        调用 LLM 生成响应。
        
        如果 LLM 管理器未配置，返回错误提示字符串。
        
        Args:
            prompt: 输入给 LLM 的提示词。
            **kwargs: 传递给 LLM 管理器的额外参数（如 temperature、max_tokens 等）。
        
        Returns:
            LLM 生成的响应文本，或错误提示（当 LLM 未配置时）。
        
        示例:
            response = self.generate("解释机器学习", temperature=0.7, max_tokens=500)
        """
        if not self._llm_manager:
            return "[Error: LLM manager not configured]"
        return self._llm_manager.generate(self._model_name, prompt, **kwargs)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        返回命令的元数据，标记需要 LLM 支持。
        
        Returns:
            包含 requires_llm=True 的元数据字典。
        """
        meta = super().get_metadata()
        meta["requires_llm"] = True
        return meta
    
    @abstractmethod
    def execute(self, ctx: Context) -> Result:
        """
        执行 LLM 命令（子类必须实现）。
        
        Args:
            ctx: 上下文对象。
        
        Returns:
            Result 对象。
        """
        pass