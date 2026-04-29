# packages/comment/src/magicc_comment/pipeline/compare_pipeline.py
from pathlib import Path
from magicc_shared.core import Context, Result
from magicc_shared.llm.client import LLMConfig, create_client
from magicc_comment.command.java.clean_command import CleanCommand
from magicc_comment.command.java.prompt_command import PromptCommand
from magicc_comment.command.java.generate_command import GenerateCommand


def run_compare_pipeline(source_path: str, work_dir: str, models: list[str]) -> dict:
    """
    运行模型对比 Pipeline
    
    Args:
        source_path: 源代码路径
        work_dir: 工作目录
        models: 模型列表，如 ["qwen-coder:1.5b", "qwen-coder:3b", "qwen-coder:7b"]
    
    Returns:
        各模型生成结果对比
    """
    source_name = Path(source_path).name
    ctx = Context()
    ctx.set("work_dir", work_dir)
    ctx.set("source_name", source_name)
    
    # 阶段1：清理（只执行一次）
    print("1. 清理代码...")
    clean_result = CleanCommand().execute(ctx)
    if not clean_result.success:
        return {"error": clean_result.message}
    
    # 阶段2：生成 Prompt（只执行一次）
    print("2. 生成 Prompts...")
    prompt_result = PromptCommand().execute(ctx)
    if not prompt_result.success:
        return {"error": prompt_result.message}
    
    # 阶段3：对每个模型执行生成
    results = {}
    for model in models:
        print(f"\n3. 使用模型: {model}")
        
        # 为每个模型创建独立的输出目录
        model_comment_dir = Path(work_dir) / source_name / "comments" / model.replace(":", "_")
        
        # 创建该模型的 GenerateCommand
        llm_config = LLMConfig(
            provider="ollama",
            model=model,
            temperature=0.3
        )
        llm_client = create_client(llm_config)
        
        # 创建新的 Context 副本（避免污染）
        model_ctx = ctx.copy()
        model_ctx.set("comment_dir", str(model_comment_dir))
        
        generate_cmd = GenerateCommand(llm_client=llm_client)
        gen_result = generate_cmd.execute(model_ctx)
        
        results[model] = {
            "success": gen_result.success,
            "message": gen_result.message,
            "comment_dir": str(model_comment_dir),
            "file_count": gen_result.data.get("comment_count", 0) if gen_result.success else 0
        }
    
    return results