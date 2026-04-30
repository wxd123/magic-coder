# magicc_shared/llm/providers/ollama_provider.py
from typing import Optional, List, Set
import subprocess
import time
import requests
from ..llm_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama 提供者实现"""
    
    def __init__(self, api_base: str = "http://localhost:11434"):
        self.api_base = api_base
        self._current_model: Optional[str] = None
        self._service_process: Optional[subprocess.Popen] = None
    
    def get_provider_name(self) -> str:
        return "ollama"
    
    def is_available(self) -> bool:
        """检查 Ollama 服务是否可用"""
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _ensure_service(self) -> bool:
        """确保服务运行（内部方法）"""
        if self.is_available():
            return True
        
        # 启动服务
        try:
            self._service_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            for _ in range(30):
                time.sleep(1)
                if self.is_available():
                    return True
            return False
        except FileNotFoundError:
            return False
    
    def ensure_model(self, model_name: str) -> bool:
        """确保模型可用"""
        if not self._ensure_service():
            return False
        
        if self._current_model == model_name:
            return True
        
        if self._current_model:
            self.unload_model(self._current_model)
        
        if not self._model_exists(model_name):
            if not self._pull_model(model_name):
                return False
        
        return self.load_model(model_name)
    
    def load_model(self, model_name: str) -> bool:
        """加载模型到内存"""
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": model_name,
                    "prompt": " ",
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=30
            )
            if response.status_code == 200:
                self._current_model = model_name
                return True
            return False
        except:
            return False
    
    def unload_model(self, model_name: str) -> bool:
        """卸载模型"""
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": model_name,
                    "prompt": " ",
                    "stream": False,
                    "options": {"num_predict": 1},
                    "keep_alive": 0
                },
                timeout=10
            )
            if response.status_code == 200:
                if self._current_model == model_name:
                    self._current_model = None
                return True
            return False
        except:
            return False
    
    def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """生成响应"""
        if not self.ensure_model(model_name):
            return f"[Error: Model {model_name} not available]"
        
        url = f"{self.api_base}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
                "num_predict": kwargs.get("max_tokens", 500),
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=kwargs.get("timeout", 60))
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            return f"[Error: {str(e)}]"
    
    def get_current_model(self) -> Optional[str]:
        return self._current_model
    
    def list_models(self) -> List[str]:
        """列出已下载的模型"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except:
            return []
    
    def _model_exists(self, model_name: str) -> bool:
        return model_name in self.list_models()
    
    def _pull_model(self, model_name: str) -> bool:
        """下载模型"""
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except:
            return False