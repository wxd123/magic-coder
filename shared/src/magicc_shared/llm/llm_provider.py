# magicc_shared/llm/llm_provider.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class LLMProvider(ABC):
    """LLM 提供者抽象接口 - 各厂商实现此接口"""
    
    @abstractmethod
    def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass
    
    @abstractmethod
    def ensure_model(self, model_name: str) -> bool:
        """确保模型可用（下载+加载）"""
        pass
    
    @abstractmethod
    def load_model(self, model_name: str) -> bool:
        """加载模型到内存"""
        pass
    
    @abstractmethod
    def unload_model(self, model_name: str) -> bool:
        """卸载模型"""
        pass
    
    @abstractmethod
    def get_current_model(self) -> Optional[str]:
        """获取当前加载的模型"""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """列出已下载的模型"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查服务是否可用"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        pass


class LLMProviderConfig(ABC):
    """提供者配置抽象"""
    
    @abstractmethod
    def validate(self) -> bool:
        pass