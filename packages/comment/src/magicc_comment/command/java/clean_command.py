# packages/comment/src/magicc_comment/command/clean_command.py
import shutil
from pathlib import Path
from magicc_shared.core import Command, Context, Result
from magicc_shared.utils import FileScanner
from magicc_comment.utils.java_comment_remover import JavaCommentRemover


class CleanCommand(Command):
    """清理Java源码注释的命令"""
    
    def execute(self, ctx: Context) -> Result:
        # 获取配置
        source_path = ctx.get("source_path")  # 原始源代码路径（如 my-project）
        work_dir = Path(ctx.get("work_dir", Path.home() / "magic_coder" / "magic_comment"))
        
        if not source_path:
            return Result.fail("source_path is required")
        
        source_name = Path(source_path).name
        source_dir = work_dir / source_name / "source"
        clean_dir = work_dir / source_name / "clean"
        
        # 1. 复制源代码到工作目录
        if source_dir.exists():
            shutil.rmtree(source_dir)
        shutil.copytree(source_path, source_dir)
        
        # 2. 扫描所有 Java 文件
        scanner = FileScanner(source_dir)
        java_files = scanner.scan_java()
        
        if not java_files:
            return Result.fail(f"No Java files found in {source_dir}")
        
        # 3. 清理注释并保存
        processed = []
        for file_info in java_files:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                original = f.read()
            
            cleaned = JavaCommentRemover.remove(original)
            
            # 输出到 clean 目录（保持目录结构）
            output_path = FileScanner.ensure_output_path(
                file_info.path, source_dir, clean_dir
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            processed.append({
                "original": str(file_info.path),
                "cleaned": str(output_path),
                "original_lines": file_info.lines,
                "cleaned_lines": len(cleaned.splitlines())
            })
        
        # 4. 存储结果到 ctx
        ctx.set("work_dir", str(work_dir))
        ctx.set("source_name", source_name)
        ctx.set("source_dir", str(source_dir))
        ctx.set("clean_dir", str(clean_dir))
        ctx.set("processed_files", processed)
        
        return Result.ok(
            data={
                "source_name": source_name,
                "source_dir": str(source_dir),
                "clean_dir": str(clean_dir),
                "file_count": len(processed),
                "total_original_lines": sum(f["original_lines"] for f in processed),
                "total_cleaned_lines": sum(f["cleaned_lines"] for f in processed)
            },
            message=f"Cleaned {len(processed)} Java files"
        )