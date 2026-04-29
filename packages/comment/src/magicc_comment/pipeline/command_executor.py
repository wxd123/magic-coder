# packages/comment/src/magicc_comment/pipeline/command_executor.py
from typing import Dict, Any, List
from magicc_shared.core import Context, Result, LLMCommand
from magicc_shared.container import get_command_with_default
from magicc_shared.llm.client import LLMConfig, create_client
from magicc_comment.pipeline.model_manager import ModelManager


class CommandExecutor:
    """负责执行 pipeline 中的命令"""
    
    def __init__(self, models_config: Dict[str, Any], default_language: str = "java"):
        self.models_config = models_config
        self.default_language = default_language
        self.model_manager = ModelManager(models_config)
    
    def execute_step(self, ctx: Context, step: Dict[str, Any]) -> Result:
        """执行单个步骤"""
        cmd_ref = step.get("command")
        if not cmd_ref:
            return Result.fail("Missing command")
        
        # 解析命令引用
        lang, cmd_name = self._parse_command_ref(cmd_ref)
        
        # 获取命令实例
        cmd = self._get_command_instance(lang, cmd_name)
        if not cmd:
            return Result.fail(f"Command not found: {lang}:{cmd_name}")
        
        # 根据命令类型分发执行
        if isinstance(cmd, LLMCommand):
            return self._execute_llm_command(cmd, ctx, step)
        else:
            return self._execute_regular_command(cmd, ctx)
    
    def _parse_command_ref(self, cmd_ref: str) -> tuple:
        """解析命令引用"""
        if ":" in cmd_ref:
            parts = cmd_ref.split(":")
            lang = parts[1] if parts[0] == "command" else parts[0]
            cmd_name = parts[-1]
        else:
            lang = self.default_language
            cmd_name = cmd_ref
        return lang, cmd_name
    
    def _get_command_instance(self, lang: str, cmd_name: str):
        """获取命令实例"""
        cmd_class = get_command_with_default(lang, cmd_name, "java")
        if cmd_class:
            return cmd_class()
        return None
    
    def _configure_llm_command(self, cmd: LLMCommand, model_ref: str) -> Result:
        """为 LLM 命令配置客户端"""
        model_config = self.models_config.get(model_ref)
        if not model_config:
            return Result.fail(f"Model not found: {model_ref}")
        
        # 获取完整模型名称
        full_model_name = model_config.get("name", model_ref) if isinstance(model_config, dict) else model_ref
        
        llm_config = LLMConfig(
            provider=model_config.get("provider", "ollama") if isinstance(model_config, dict) else "ollama",
            model=full_model_name,
            temperature=model_config.get("temperature", 0.3) if isinstance(model_config, dict) else 0.3,
            max_tokens=model_config.get("max_tokens", 500) if isinstance(model_config, dict) else 500,
        )
        cmd.set_llm_client(create_client(llm_config), model_ref)
        return Result.ok()
    
    

    def _execute_llm_command(self, cmd: LLMCommand, ctx: Context, step: Dict[str, Any]) -> Result:
        """执行 LLM 命令（支持多模型依次执行）"""
        # 获取模型列表
        models = step.get("models", []) or ([step.get("model_ref")] if step.get("model_ref") else [])
        if not models:
            return Result.fail("LLM command requires 'models' or 'model_ref'")
        
        # 将任务信息注入到 context
        task_info = {
            "command": step.get("command", "unknown"),
            "models": models,
            "description": step.get("description", ""),
            "step_index": ctx.get("step_index", 0)
        }
        ctx.set("current_task", task_info)
        
        all_results = []
        
        # 依次使用每个模型执行
        for model_ref in models:
            print(f"\n{'='*60}")
            print(f"使用模型: {model_ref}")
            print(f"{'='*60}")
            
            # 更新任务信息中的当前模型
            task_info["current_model"] = model_ref
            ctx.set("current_task", task_info)
            
            # 1. 确保模型可用
            model_result = self.model_manager.ensure_model_available(model_ref)
            if not model_result.success:
                return Result.fail(f"Model preparation failed for {model_ref}: {model_result.message}")
            
            # 2. 配置 LLM 客户端
            config_result = self._configure_llm_command(cmd, model_ref)
            if not config_result.success:
                return config_result
            
            # 3. 执行命令
            result = cmd.execute(ctx)
            
            # 记录结果
            all_results.append({
                "model": model_ref,
                "success": result.success,
                "data": result.data if result.success else None,
                "message": result.message
            })
            
            if not result.success:
                return Result.fail(f"Command failed for model {model_ref}: {result.message}")
            
            print(f"✅ 模型 {model_ref} 执行完成\n")
        
        # 清除任务信息
        ctx.set("current_task", None)
        
        # 所有模型都执行成功
        return Result.ok(
            data={"results": all_results},
            message=f"Executed with {len(models)} models"
        )
    
    def _execute_regular_command(self, cmd, ctx: Context, step: Dict[str, Any] = None) -> Result:
        """执行普通命令（非 LLM 命令）"""
        # 对于普通命令，也可以注入任务信息
        if step:
            task_info = {
                "command": step.get("command", "unknown"),
                "description": step.get("description", ""),
                "step_index": ctx.get("step_index", 0)
            }
            ctx.set("current_task", task_info)
        
        # 执行命令
        result = cmd.execute(ctx)
        
        # 清除任务信息
        ctx.set("current_task", None)
        
        return result
    
    def release_resources(self) -> Result:
        """释放所有模型资源"""
        if hasattr(self, 'model_manager'):
            return self.model_manager.release_all_models()
        return Result.ok()