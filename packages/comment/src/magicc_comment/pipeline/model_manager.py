# packages/comment/src/magicc_comment/pipeline/model_manager.py
from typing import Dict, Any, Set, List, Optional
from magicc_shared.core import Result
from magicc_shared.llm.ollama_manager import get_ollama_manager


class ModelManager:
    """负责管理 LLM 模型的下载、启动和停止"""
    
    def __init__(self, models_config: Dict[str, Any]):
        self.models_config = models_config
        self.ollama_manager = get_ollama_manager()
        self.current_model: Optional[str] = None
    
    def collect_needed_models(self, pipeline: List[Dict[str, Any]]) -> Set[str]:
        """从 pipeline 步骤中收集需要的所有模型"""
        models_needed = set()
        for step in pipeline:
            models_needed.update(step.get("models", []))
            if "model_ref" in step:
                models_needed.add(step["model_ref"])
        return models_needed
    
    def _get_full_model_name(self, model_ref: str) -> Optional[str]:
        """将模型引用转换为完整的模型名称"""
        model_config = self.models_config.get(model_ref)
        if model_config and isinstance(model_config, dict):
            if model_config.get("provider") == "ollama":
                return model_config.get("name", model_ref)
        return None
    
    def _stop_current_model(self) -> None:
        """停止当前正在运行的模型"""
        if self.current_model:
            print(f"🛑 停止当前模型: {self.current_model}")
            self.ollama_manager.stop_model(self.current_model)
            self.current_model = None
    
    def _ensure_model_downloaded(self, full_name: str) -> Result:
        """确保模型已下载"""
        if not self.ollama_manager.is_model_available(full_name):
            print(f"📥 下载模型: {full_name}")
            if not self.ollama_manager.pull_model(full_name):
                return Result.fail(f"Failed to pull {full_name}")
        return Result.ok()
    
    def _start_model(self, full_name: str) -> Result:
        """启动模型"""
        print(f"🚀 启动模型: {full_name}")
        if not self.ollama_manager.start_model(full_name):
            return Result.fail(f"Failed to start model: {full_name}")
        self.current_model = full_name
        return Result.ok()
    
    def _verify_model_ready(self, full_name: str, max_retries: int = 30) -> Result:
        """验证模型已成功启动"""
        import time
        
        for _ in range(max_retries):
            running_models = self.ollama_manager.get_running_models()
            if full_name in running_models:
                print(f"✅ 模型已就绪: {full_name}")
                return Result.ok()
            time.sleep(1)
        
        return Result.fail(f"Model not ready after {max_retries}s: {full_name}")
    
    def ensure_model_available(self, model_ref: str) -> Result:
        """
        确保指定的模型已下载并运行
        
        流程：
        1. 启动 Ollama 服务
        2. 如果当前有运行的模型且不是需要的模型，停止它
        3. 下载模型（如果缺失）
        4. 启动模型
        5. 验证模型已就绪
        """
        # 1. 启动 Ollama 服务
        if not self.ollama_manager.start():
            return Result.fail("Failed to start Ollama")
        
        # 2. 获取完整模型名称
        full_name = self._get_full_model_name(model_ref)
        if not full_name:
            return Result.fail(f"Invalid model reference: {model_ref}")
        
        # 3. 如果当前模型就是需要的模型，直接返回成功
        if self.current_model == full_name:
            print(f"✅ 模型已运行: {full_name}")
            return Result.ok()
        
        # 4. 停止当前运行的模型
        if self.current_model:
            self._stop_current_model()
        
        # 5. 确保模型已下载
        download_result = self._ensure_model_downloaded(full_name)
        if not download_result.success:
            return download_result
        
        # 6. 启动模型
        start_result = self._start_model(full_name)
        if not start_result.success:
            return start_result
        
        # 7. 验证模型已就绪
        verify_result = self._verify_model_ready(full_name)
        if not verify_result.success:
            return verify_result
        
        return Result.ok(message=f"Model ready: {full_name}")
    
    def stop_all_models(self) -> Result:
        """停止所有模型"""
        if self.current_model:
            self._stop_current_model()
        return Result.ok(message="All models stopped")
    
    def release_all_models(self) -> Result:
        """释放所有模型资源"""
        print("   🧹 清理模型资源...")
        
        if self.current_model:
            print(f"   🛑 停止模型: {self.current_model}")
            self.ollama_manager.stop_model(self.current_model)
            self.current_model = None
        
        # 可选：如果需要完全停止 Ollama 服务（通常不需要）
        # 取消注释下面的代码会停止 Ollama 服务
        # if self.ollama_manager.is_running():
        #     print("   🛑 停止 Ollama 服务")
        #     self.ollama_manager.stop()
        
        print("   ✅ 资源清理完成")
        return Result.ok(message="All models released")