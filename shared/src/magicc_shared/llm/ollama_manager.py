# magicc_shared/llm/ollama_manager.py

import subprocess
import time
import requests
import psutil
from typing import Optional, List, Set
from dataclasses import dataclass


@dataclass
class ModelInfo:
    name: str
    size: str
    modified: str


class OllamaManager:
    """Ollama 模型管理器 - 负责模型的启动、停止、切换"""
    
    def __init__(self, api_base: str = "http://localhost:11434"):
        self.api_base = api_base
        self.current_model: Optional[str] = None
        self.process: Optional[subprocess.Popen] = None
    
    def is_running(self) -> bool:
        """检查 Ollama 服务是否运行"""
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start(self) -> bool:
        """启动 Ollama 服务"""
        if self.is_running():
            print("   ✅ Ollama 已在运行")
            return True
        
        print("   🚀 启动 Ollama...")
        try:
            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # 等待启动
            for _ in range(30):
                time.sleep(1)
                if self.is_running():
                    print("   ✅ Ollama 启动成功")
                    return True
            print("   ❌ Ollama 启动超时")
            return False
        except FileNotFoundError:
            print("   ❌ Ollama 未安装，请访问 https://ollama.com 下载安装")
            return False
    
    def stop(self):
        """停止 Ollama 服务"""
        if self.process:
            self.process.terminate()
            self.process = None
    
    def get_loaded_model(self) -> Optional[str]:
        """获取当前加载到显存的模型"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] == 'ollama':
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'run' in cmdline:
                        parts = cmdline.split()
                        for i, part in enumerate(parts):
                            if part == 'run' and i + 1 < len(parts):
                                return parts[i + 1]
            return None
        except:
            return None
    
    def stop_current_model(self) -> bool:
        """停止当前加载的模型"""
        current = self.get_loaded_model()
        if not current:
            print("   ℹ️ 没有正在运行的模型")
            return True
        
        print(f"   🛑 停止当前模型: {current}")
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'ollama':
                    proc.terminate()
                    proc.wait(timeout=5)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"   ⚠️ 停止模型失败: {e}")
            return False
    
    def load_model(self, model_name: str) -> bool:
        """加载指定模型到显存"""
        print(f"   📥 加载模型: {model_name}")
        
        if not self._model_exists(model_name):
            print(f"   📦 模型不存在，开始下载...")
            if not self._pull_model(model_name):
                return False
        
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
                print(f"   ✅ 模型加载成功: {model_name}")
                self.current_model = model_name
                return True
            else:
                print(f"   ❌ 模型加载失败: {response.text}")
                return False
        except requests.exceptions.Timeout:
            print(f"   ❌ 模型加载超时")
            return False
        except Exception as e:
            print(f"   ❌ 模型加载异常: {e}")
            return False
    
    def ensure_model(self, model_name: str) -> bool:
        """确保指定模型已加载"""
        print(f"\n🔧 准备模型: {model_name}")
        
        # 1. 检查并启动 Ollama
        if not self.is_running():
            if not self.start():
                return False
        
        # 2. 检查当前加载的模型
        current_model = self.get_loaded_model()
        print(f"   📍 当前模型: {current_model or '无'}")
        
        # 3. 如果模型不匹配，停止当前模型
        if current_model and current_model != model_name:
            print(f"   🔄 模型不匹配，需要切换")
            if not self.stop_current_model():
                return False
            time.sleep(2)
        elif current_model == model_name:
            print(f"   ✅ 模型已加载，无需操作")
            return True
        
        # 4. 加载所需模型
        if not self.load_model(model_name):
            return False
        
        # 5. 确认加载成功
        time.sleep(1)
        loaded_model = self.get_loaded_model()
        if loaded_model == model_name:
            print(f"   ✅ 确认模型已加载: {model_name}")
            return True
        else:
            print(f"   ❌ 模型加载确认失败: 期望 {model_name}, 实际 {loaded_model}")
            return False
    
    def _model_exists(self, model_name: str) -> bool:
        """检查模型是否已下载"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            models = response.json().get("models", [])
            for m in models:
                if m["name"] == model_name:
                    return True
            return False
        except:
            return False
    
    def _pull_model(self, model_name: str) -> bool:
        """下载模型"""
        print(f"   📥 下载模型 {model_name}...")
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print(f"   ✅ 下载完成")
                return True
            else:
                print(f"   ❌ 下载失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ 下载异常: {e}")
            return False

    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否已下载"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            models = response.json().get("models", [])
            for m in models:
                if m["name"] == model_name:
                    return True
            return False
        except:
            return False
    
    # ========== 新增函数 ==========
    
    def get_running_models(self) -> Set[str]:
        """获取当前正在运行的模型列表"""
        running_models = set()
        try:
            # 使用 ollama ps 命令获取运行中的模型
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # 跳过标题行
                    for line in lines[1:]:
                        if line.strip():
                            # 格式: NAME ID SIZE PROCESSOR CONTEXT UNTIL
                            parts = line.split()
                            if parts:
                                running_models.add(parts[0])
        except Exception:
            pass
        return running_models
    
    def stop_model(self, model_name: str) -> bool:
        """停止指定的模型"""
        try:
            # 通过发送 keep_alive=0 来停止模型
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
            return response.status_code == 200
        except Exception:
            return False
    
    def start_model(self, model_name: str) -> bool:
        """启动指定的模型（加载到内存）"""
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
            return response.status_code == 200
        except Exception:
            return False

# 全局管理器
_ollama_manager: Optional[OllamaManager] = None


def get_ollama_manager() -> OllamaManager:
    global _ollama_manager
    if _ollama_manager is None:
        _ollama_manager = OllamaManager()
    return _ollama_manager