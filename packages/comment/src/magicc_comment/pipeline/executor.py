# packages/comment/src/magicc_comment/pipeline/executor.py
from typing import Dict, Any
from magicc_shared.core import Context, Result
from magicc_comment.command.container import regist_command
from magicc_comment.pipeline.command_executor import CommandExecutor


class PipelineExecutor:
    """
    Pipeline 执行器，负责协调整个注释生成流程。
    
    该执行器专门为 Java 代码注释生成场景设计，支持从配置文件中加载
    Pipeline 定义，按顺序执行命令（如 clean、generate、report），
    并自动管理多模型资源的分配与释放。
    
    主要功能:
        1. 根据配置初始化执行环境
        2. 注册指定语言的命令
        3. 按顺序执行 Pipeline 中定义的步骤
        4. 自动释放模型资源（无论成功或失败）
    
    示例(pipeline.yaml): 
        ```yaml
        name: "comment-generation-pipeline"
        language: "java"
        
        # 模型池配置
        models:
          qwen_0.5b:
            provider: ollama
            name: qwen2.5-coder:0.5b
            temperature: 0.1
            
        # Pipeline 步骤定义
        pipeline:
        - command: java:clean          # 清理步骤
        - command: java:generate        # 生成步骤，可指定多个模型
            models: ["qwen_0.5b", "qwen_1.5b"]
        - command: java:report          # 报告步骤
        ```
    
    注意:
        执行完成后会自动调用 _release_resources() 释放模型资源
        即使发生异常也会执行资源清理
        generate 步骤的 models 字段为可选，未指定则使用命令默认模型
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 Pipeline 执行器。

        根据配置设置语言环境，注册对应语言的命令，并初始化命令执行器。

        Args:
            config: 配置字典，通常从 pipeline.yaml 加载，应包含以下键：
                - language: 编程语言标识（如 "java", "python"），默认为 "java"
                - models: 模型池配置字典，定义可用模型及其参数
                - pipeline: Pipeline 步骤列表，每个步骤为包含 command 字段的字典
        
        示例:
            config = {
                "language": "java",
                "models": {
                    "qwen_0.5b": {
                        "provider": "ollama",
                        "name": "qwen2.5-coder:0.5b",
                        "temperature": 0.1
                    }
                    ...                
                },
                "pipeline": [
                    {"command": "java:clean"},
                    {"command": "java:generate", "models": ["qwen_0.5b"]},
                    {"command": "java:report"},
                    ... 
                ]
            }
            executor = PipelineExecutor(config)            
        """
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
        """    
        从配置中获取 Pipeline 步骤列表，按顺序执行每个步骤。
        步骤格式支持两种形式：
            - 字符串格式（向后兼容）: "java:clean"
            - 字典格式（推荐）: {"command": "java:generate", "models": ["qwen_0.5b"]}
        
        如果任何步骤执行失败，立即返回失败结果，不再执行后续步骤。
        无论执行成功还是失败，最终都会释放模型资源。
        
        Args:
            ctx: 上下文对象，包含 Pipeline 执行所需的输入数据
            pipeline_name: Pipeline 配置的名称，默认为 "pipeline"
        
        Returns:
            Result 对象:
                - 成功: Result.ok(message="Pipeline completed")
                - 失败: Result.fail(message="错误描述")
        
        示例:
            >>> # 使用默认 pipeline 名称
            >>> result = executor.run(ctx)
            
            >>> # 检查执行结果
            >>> if not result.success:
            ...     print(f"Pipeline 执行失败: {result.message}")
        
        注意:
            - 方法使用 finally 块确保资源被正确释放
            - 多模型配置会在 generate 步骤中依次使用每个模型
        """
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
        """
        释放模型资源（内部方法）。
        
        释放命令执行器中占用的所有模型资源，如 LLM 连接、缓存等。
        此方法会在 run 方法的 finally 块中自动调用。
        
        资源释放包括:
            - 关闭 LLM 客户端连接
            - 清理临时文件
            - 释放内存中的模型缓存
        
        示例输出:
            ============================================================
            Pipeline 执行结束，释放模型资源...
        
        注意:
            仅在命令执行器实现了 release_resources 方法时才会执行释放操作。
            如果没有实现该方法，跳过释放步骤（不报错）。
        """
        if hasattr(self.command_executor, 'release_resources'):
            print("\n" + "="*60)
            print("Pipeline 执行结束，释放模型资源...")
            self.command_executor.release_resources()