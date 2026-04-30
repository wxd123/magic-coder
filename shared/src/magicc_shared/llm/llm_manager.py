# magicc_shared/llm/llm_manager.py
from typing import Dict, Optional, Any
from .llm_provider import LLMProvider
from magicc_shared.llm.providers.ollama_provider import OllamaProvider


class LLMManager:
    """
    LLM 管理器 - 统一入口
    
    职责：
    1. 管理多个 Provider
    2. 提供统一的调用接口
    3. 代理 Provider 的方法调用
    """
    
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._default_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: LLMProvider, set_as_default: bool = False):
        """注册提供者"""
        self._providers[name] = provider
        if set_as_default or self._default_provider is None:
            self._default_provider = name
    
    def get_provider(self, name: str = None) -> Optional[LLMProvider]:
        """获取提供者"""
        provider_name = name or self._default_provider
        if not provider_name:
            return None
        return self._providers.get(provider_name)
    
    def set_default_provider(self, name: str):
        """设置默认提供者"""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not registered")
        self._default_provider = name
    
    # ========== 代理方法 ==========
    
    def generate(self, model_name: str, prompt: str, provider: str = None, **kwargs) -> str:
        """生成响应"""
        p = self.get_provider(provider)
        if not p:
            return "[Error: No provider available]"
        return p.generate(model_name, prompt, **kwargs)
    
    def ensure_model(self, model_name: str, provider: str = None) -> bool:
        """确保模型可用"""
        p = self.get_provider(provider)
        if not p:
            return False
        return p.ensure_model(model_name)
    
    def load_model(self, model_name: str, provider: str = None) -> bool:
        """加载模型"""
        p = self.get_provider(provider)
        if not p:
            return False
        return p.load_model(model_name)
    
    def unload_model(self, model_name: str, provider: str = None) -> bool:
        """卸载模型"""
        p = self.get_provider(provider)
        if not p:
            return False
        return p.unload_model(model_name)
    
    def get_current_model(self, provider: str = None) -> Optional[str]:
        """获取当前模型"""
        p = self.get_provider(provider)
        if not p:
            return None
        return p.get_current_model()
    
    def list_models(self, provider: str = None) -> list:
        """列出已下载模型"""
        p = self.get_provider(provider)
        if not p:
            return []
        return p.list_models()
    
    def is_available(self, provider: str = None) -> bool:
        """检查服务是否可用"""
        p = self.get_provider(provider)
        if not p:
            return False
        return p.is_available()
    
    def get_provider_names(self) -> list:
        """获取所有已注册的提供者名称"""
        return list(self._providers.keys())
    
    def switch_model(self, model_name: str, provider: str = None) -> bool:
        """切换模型（ensure_model 的别名）"""
        return self.ensure_model(model_name, provider)


# 全局单例
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """获取全局 LLM 管理器（单例）"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
        # 默认注册 Ollama
        _llm_manager.register_provider("ollama", OllamaProvider(), set_as_default=True)
    return _llm_manager


def reset_llm_manager():
    """重置管理器（用于测试）"""
    global _llm_manager
    _llm_manager = None