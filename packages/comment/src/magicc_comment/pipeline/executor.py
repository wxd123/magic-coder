# packages/comment/src/magicc_comment/pipeline/executor.py
from typing import Dict, Any
from magicc_shared.core import Context, Result
from magicc_comment.command.container import regist_command
from magicc_comment.pipeline.model_manager import ModelManager
from magicc_comment.pipeline.command_executor import CommandExecutor


class PipelineExecutor:
    """Pipeline 执行器，负责协调整个流程"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.language = config.get("language", "java")
        
        # 注册命令
        regist_command(self.language)
        
        # 初始化命令执行器
        self.command_executor = CommandExecutor(
            models_config=config.get("models", {}),
            default_language=self.language
        )
    
    def run(self, ctx: Context, pipeline_name: str = "pipeline") -> Result:
        """运行 pipeline"""
        try:
            # 获取 pipeline 配置
            pipeline = self.config.get(pipeline_name)
            if not pipeline:
                return Result.fail(f"Pipeline '{pipeline_name}' not found")
            
            # 执行 pipeline 中的每个步骤
            for step in pipeline:
                result = self.command_executor.execute_step(ctx, step)
                if not result.success:
                    return result
            
            return Result.ok(message="Pipeline completed")
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()
    
    def _release_resources(self):
        """释放模型资源"""
        if hasattr(self.command_executor, 'release_resources'):
            print("\n" + "="*60)
            print("Pipeline 执行结束，释放模型资源...")
            self.command_executor.release_resources()