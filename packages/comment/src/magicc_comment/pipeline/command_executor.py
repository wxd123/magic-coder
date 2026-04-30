# packages/comment/src/magicc_comment/pipeline/command_executor.py
from typing import Dict, Any, List, Optional
from magicc_shared.core import Context, Result, LLMCommand
from magicc_shared.container import get_command_with_default
from magicc_shared.llm.llm_manager import get_llm_manager


class CommandExecutor:
    """负责执行 pipeline 中的命令"""
    
    def __init__(self, models_config: Dict[str, Any], default_language: str = "java"):
        """
        初始化命令执行器
        
        Args:
            models_config: 模型配置字典，键为模型引用名，值为模型配置（包含模型名称等）
            default_language: 默认编程语言，当命令引用中没有指定语言时使用，默认为 "java"
        """
        self.models_config = models_config
        self.default_language = default_language
        
        # 使用全局 LLM 管理器
        self.llm_manager = get_llm_manager()
        
        # 缓存命令实例
        self._command_cache: Dict[str, LLMCommand] = {}
    
    def execute_step(self, ctx: Context, step: Dict[str, Any]) -> Result:
        """
        执行单个步骤
        
        Args:
            ctx: 执行上下文，包含当前执行状态和数据
            step: 步骤配置字典，必须包含 "command" 字段，可选包含 "models"、"model_ref"、"description" 等
            
        Returns:
            Result: 执行结果，成功时包含执行数据，失败时包含错误信息
            
        Note:
            支持两种命令类型：
            1. LLMCommand: 需要调用大语言模型执行的命令，支持多模型依次执行
            2. 普通命令: 不需要 LLM 的常规命令，直接执行
        """
        cmd_ref = step.get("command")
        if not cmd_ref:
            return Result.fail("Missing command")
        
        lang, cmd_name = self._parse_command_ref(cmd_ref)
        
        cmd = self._get_command_instance(lang, cmd_name)
        if not cmd:
            return Result.fail(f"Command not found: {lang}:{cmd_name}")
        
        if isinstance(cmd, LLMCommand):
            return self._execute_llm_command(cmd, ctx, step)
        else:
            return self._execute_regular_command(cmd, ctx, step)
    
    def _parse_command_ref(self, cmd_ref: str) -> tuple:
        """
        解析命令引用字符串
        
        Args:
            cmd_ref: 命令引用，格式可以是：
                    - "command:language:command_name" (完整格式)
                    - "language:command_name" (简洁格式)
                    - "command_name" (使用默认语言)
                    
        Returns:
            tuple: (语言名称, 命令名称)
        """
        if ":" in cmd_ref:
            parts = cmd_ref.split(":")
            # 如果第一部分是 "command"，则跳过，取第二部分作为语言
            lang = parts[1] if parts[0] == "command" else parts[0]
            cmd_name = parts[-1]
        else:
            lang = self.default_language
            cmd_name = cmd_ref
        return lang, cmd_name
    
    def _get_command_instance(self, lang: str, cmd_name: str):
        """
        获取命令实例（带缓存）
        
        Args:
            lang: 编程语言名称
            cmd_name: 命令名称
            
        Returns:
            命令实例，如果未找到则返回 None
            
        Note:
            使用缓存机制避免重复创建命令实例，提高性能
        """
        cache_key = f"{lang}:{cmd_name}"
        if cache_key in self._command_cache:
            return self._command_cache[cache_key]
        
        cmd_class = get_command_with_default(lang, cmd_name, "java")
        if cmd_class:
            cmd = cmd_class()
            self._command_cache[cache_key] = cmd
            return cmd
        return None
    
    def _get_full_model_name(self, model_ref: str) -> Optional[str]:
        """
        将模型引用转换为完整的模型名称
        
        Args:
            model_ref: 模型引用名（配置中的键名）
            
        Returns:
            Optional[str]: 完整的模型名称，如果配置中没有则返回原引用名
        """
        model_config = self.models_config.get(model_ref)
        if model_config and isinstance(model_config, dict):
            return model_config.get("name", model_ref)
        return model_ref
    
    def _optimize_model_order(self, models: List[str]) -> List[str]:
        """
        优化模型执行顺序，优先使用已加载的模型
        
        Args:
            models: 模型引用名列表
            
        Returns:
            List[str]: 优化后的模型列表，当前已加载的模型会被移到列表首位
            
        Note:
            这样设计可以避免重复加载模型，提高执行效率
        """
        current_model = self.llm_manager.get_current_model()
        
        if current_model and current_model in models:
            optimized = [current_model]
            optimized.extend([m for m in models if m != current_model])
            print(f"📌 当前模型 {current_model} 已在运行，优先执行")
            return optimized
        
        return models
    
    def _execute_llm_command(self, cmd: LLMCommand, ctx: Context, step: Dict[str, Any]) -> Result:
        """
        执行 LLM 命令（支持多模型依次执行）
        
        Args:
            cmd: LLM 命令实例
            ctx: 执行上下文
            step: 步骤配置，必须包含 "models" 或 "model_ref" 字段
            
        Returns:
            Result: 执行结果，成功时包含所有模型的执行结果列表，失败时包含错误信息
            
        Note:
            执行流程：
            1. 获取模型列表并优化执行顺序
            2. 对每个模型：
               a. 确保模型可用（必要时加载）
               b. 注入 LLM 管理器到命令
               c. 执行命令
               d. 记录执行结果
            3. 如果任一模型执行失败，立即返回失败
            4. 执行完成后释放资源
        """
        # 获取模型列表
        models = step.get("models", []) or ([step.get("model_ref")] if step.get("model_ref") else [])
        if not models:
            return Result.fail("LLM command requires 'models' or 'model_ref'")
        
        # 优化模型执行顺序
        models = self._optimize_model_order(models)
        
        task_info = {
            "command": step.get("command", "unknown"),
            "models": models,
            "description": step.get("description", ""),
            "step_index": ctx.get("step_index", 0)
        }
        ctx.set("current_task", task_info)
        
        all_results = []
        
        try:
            for idx, model_ref in enumerate(models):
                print(f"\n{'='*60}")
                print(f"使用模型 [{idx+1}/{len(models)}]: {model_ref}")
                print(f"{'='*60}")
                
                task_info["current_model"] = model_ref
                ctx.set("current_task", task_info)
                
                full_model_name = self._get_full_model_name(model_ref)
                if not full_model_name:
                    return Result.fail(f"Invalid model reference: {model_ref}")
                
                # 1. 确保模型可用
                print(f"🔧 准备模型: {full_model_name}")
                if not self.llm_manager.ensure_model(full_model_name):
                    return Result.fail(f"Failed to ensure model: {model_ref}")
                
                print(f"✅ 模型已就绪: {full_model_name}")
                
                # 2. 注入 LLM 管理器到命令
                cmd.set_llm_manager(self.llm_manager, full_model_name)
                
                # 3. 执行命令
                result = cmd.execute(ctx)
                
                all_results.append({
                    "model": model_ref,
                    "full_model_name": full_model_name,
                    "success": result.success,
                    "data": result.data if result.success else None,
                    "message": result.message
                })
                
                if not result.success:
                    return Result.fail(f"Command failed for model {model_ref}: {result.message}")
                
                print(f"✅ 模型 {model_ref} 执行完成\n")
        
        except Exception as e:
            current = self.llm_manager.get_current_model()
            if current:
                self.llm_manager.unload_model(current)
            return Result.fail(f"Unexpected error: {e}")
        
        finally:
            ctx.set("current_task", None)
        
        return Result.ok(
            data={"results": all_results},
            message=f"Executed with {len(models)} models"
        )
    
    def _execute_regular_command(self, cmd, ctx: Context, step: Dict[str, Any] = None) -> Result:
        """
        执行普通命令（非 LLM 命令）
        
        Args:
            cmd: 命令实例（非 LLMCommand 类型）
            ctx: 执行上下文
            step: 步骤配置字典（可选），用于记录任务信息
            
        Returns:
            Result: 命令执行结果
        """
        if step:
            task_info = {
                "command": step.get("command", "unknown"),
                "description": step.get("description", ""),
                "step_index": ctx.get("step_index", 0)
            }
            ctx.set("current_task", task_info)
        
        result = cmd.execute(ctx)
        ctx.set("current_task", None)
        
        return result
    
    def release_resources(self) -> Result:
        """
        释放所有模型资源
        
        Returns:
            Result: 资源释放结果
            
        Note:
            执行以下清理工作：
            1. 清空命令实例缓存
            2. 卸载当前加载的模型（如果有）
        """
        self._command_cache.clear()
        
        current_model = self.llm_manager.get_current_model()
        if current_model:
            self.llm_manager.unload_model(current_model)
        
        return Result.ok(message="Resources released")