# packages/comment/src/magicc_comment/command/generate_command.py

from pathlib import Path
from typing import Optional, List, Dict, Any
from magicc_shared.core import LLMCommand, Context, Result
from magicc_shared.utils import FileScanner
from magicc_comment.utils.progress_display import ProgressDisplay
import sys
import time


class GenerateCommand(LLMCommand):
    """
    生成注释命令
    
    支持两种模式：
    1. 单模型：使用 model_ref
    2. 多模型：使用 models 数组
    """
    
    def __init__(self):
        super().__init__()
        self.progress_display = ProgressDisplay()
    
    def _print_progress(self, current_file: int, total_files: int, 
                       current_func: int, total_funcs: int,
                       filename: str, success: bool = True, error_msg: str = None,
                       is_last: bool = False):
        """打印进度信息（委托给 ProgressDisplay）"""
        self.progress_display.update_progress(
            current_file=current_file,
            total_files=total_files,
            current_func=current_func,
            total_funcs=total_funcs,
            filename=filename,
            success=success,
            error_msg=error_msg,
            is_last=is_last
        )
    
    def set_task_info(self, task_info: Dict[str, Any]):
        """设置任务信息（由 executor 调用）"""
        self.progress_display.set_task(task_info)
    
    def execute(self, ctx: Context) -> Result:
        # 从 context 获取任务信息（如果已设置）
        task_info = ctx.get("current_task")
        if task_info:
            self.set_task_info(task_info)
        
        # 从父类获取 LLM 客户端
        llm_client = self.get_llm_client()
        if llm_client is None:
            return Result.fail("LLM client not injected")
        
        model_name = self.get_model_name()
        
        work_dir = ctx.get("work_dir")
        source_name = ctx.get("source_name")
        
        if not work_dir or not source_name:
            return Result.fail("work_dir and source_name are required")
        
        work_dir = Path(work_dir)
        
        # 确定输出目录
        output_dir = ctx.get("comment_dir")
        if not output_dir:
            # 使用模型名称作为子目录
            model_dir = model_name or "default"
            model_dir = model_dir.replace(":", "_").replace("/", "_")
            output_dir = work_dir / source_name / "comments" / model_dir
        else:
            output_dir = Path(output_dir)
        
        prompt_dir = work_dir / source_name / "prompt"
        
        if not prompt_dir.exists():
            return Result.fail(f"Prompt directory not found: {prompt_dir}")
        
        # 扫描所有 prompt 文件
        scanner = FileScanner(prompt_dir)
        prompt_files = scanner.scan({".prompt"})
        
        if not prompt_files:
            return Result.fail(f"No prompt files found in {prompt_dir}")
        
        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成注释
        comments = []
        total_files = len(prompt_files)
        
        for file_idx, file_info in enumerate(prompt_files, 1):
            try:
                # 读取 prompt
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    prompt = f.read()
                
                # 显示开始处理
                self._print_progress(
                    current_file=file_idx,
                    total_files=total_files,
                    current_func=0,
                    total_funcs=1,
                    filename=file_info.name,
                    success=True,
                    is_last=False
                )
                
                # 调用 LLM 生成注释
                comment = llm_client.generate(prompt)
                
                # 更新进度
                self._print_progress(
                    current_file=file_idx,
                    total_files=total_files,
                    current_func=1,
                    total_funcs=1,
                    filename=file_info.name,
                    success=True,
                    is_last=(file_idx == total_files)
                )
                
                # 输出路径
                relative_path = file_info.path.relative_to(prompt_dir)
                comment_path = output_dir / relative_path.with_suffix(".comment")
                comment_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(comment_path, 'w', encoding='utf-8') as f:
                    f.write(comment)
                
                comments.append({
                    "source": str(file_info.path),
                    "output": str(comment_path),
                    "length": len(comment)
                })
                
            except Exception as e:
                error_msg = str(e)
                is_last_file = (file_idx == total_files)
                self._print_progress(
                    current_file=file_idx,
                    total_files=total_files,
                    current_func=1,
                    total_funcs=1,
                    filename=file_info.name,
                    success=False,
                    error_msg=error_msg[:15],
                    is_last=is_last_file
                )
                return Result.fail(f"LLM call failed for {file_info.name}: {error_msg}")
        
        # 存储结果
        ctx.set("comment_dir", str(output_dir))
        ctx.set("comments", comments)
        if model_name:
            ctx.set(f"comments_{model_name}", comments)
        
        return Result.ok(
            data={
                "comment_count": len(comments),
                "comment_dir": str(output_dir),
                "model": model_name
            },
            message=f"Generated {len(comments)} comments using {model_name or 'unknown'}"
        )