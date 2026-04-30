# packages/comment/src/magicc_comment/command/clean_command.py
import shutil
from pathlib import Path
from magicc_shared.core import Command, Context, Result
from magicc_shared.utils import FileScanner
from magicc_comment.utils.java_comment_remover import JavaCommentRemover


class CleanCommand(Command):
    """
    清理Java源码注释的命令
    
    该命令负责从 Java 源代码中移除所有注释（包括单行注释、多行注释和 Javadoc 注释），
    并将处理后的代码保存到工作目录中，为后续的注释生成步骤提供干净的代码基础。
    
    主要功能：
        1. 复制原始源代码到工作目录
        2. 扫描所有 Java 文件
        3. 移除代码中的注释
        4. 保持原始目录结构保存清理后的文件
    
    工作流程：
        原始路径 (source_path) 
            ↓ 复制
        工作目录/source_name/source/
            ↓ 清理注释
        工作目录/source_name/clean/
            ↓ 供后续命令使用
    
    使用示例：
        command = CleanCommand()
        context = Context({
            "source_path": "/path/to/my-project",
            "work_dir": "/path/to/work"
        })
        result = command.execute(context)
        
    Note:
        清理后的代码仅用于分析和方法提取，不会影响原始源代码。
        删除注释后，代码的行数会减少，这将被记录下来供统计使用。
    """
    
    def execute(self, ctx: Context) -> Result:
        """
        执行清理命令
        
        核心步骤：
            1. 验证并获取配置参数
            2. 复制源代码到工作目录
            3. 扫描所有 Java 文件
            4. 移除每个文件中的注释
            5. 保存清理后的文件到 clean 目录
            6. 将处理结果和路径信息存储到上下文中
        
        Args:
            ctx: 执行上下文，必须包含以下键值：
                - source_path: 原始源代码的路径（必需）
                - work_dir: 工作目录路径（可选，默认为 ~/magic_coder/magic_comment）
                
        Returns:
            Result: 执行结果对象
                - 成功时：data 包含源名称、目录路径、文件数、代码行数统计等信息
                - 失败时：message 包含错误信息
                
        上下文输出（通过 ctx.set 存储）：
            - work_dir: 工作目录路径
            - source_name: 源代码项目名称
            - source_dir: 原始代码复制后的目录路径（source 目录）
            - clean_dir: 清理后的代码目录路径（clean 目录）
            - processed_files: 处理过的文件列表，每个文件包含原始路径、清理后路径、原始行数、清理后行数
        
        Example:
            >>> ctx = Context({"source_path": "/project/my-app", "work_dir": "/tmp/magic"})
            >>> result = CleanCommand().execute(ctx)
            >>> if result.success:
            ...     print(f"Cleaned {result.data['file_count']} files")
            ...     print(f"Removed {result.data['total_original_lines'] - result.data['total_cleaned_lines']} lines")
            Cleaned 42 files
            Removed 156 lines
        """
        # 获取配置
        source_path = ctx.get("source_path")  # 原始源代码路径（如 my-project）
        work_dir = Path(ctx.get("work_dir", Path.home() / "magic_coder" / "magic_comment"))
        
        if not source_path:
            return Result.fail("source_path is required")
        
        source_name = Path(source_path).name
        source_dir = work_dir / source_name / "source"
        clean_dir = work_dir / source_name / "clean"
        
        # 1. 复制源代码到工作目录
        # 确保从干净的副本开始，避免残留文件
        if source_dir.exists():
            shutil.rmtree(source_dir)
        shutil.copytree(source_path, source_dir)
        
        # 2. 扫描所有 Java 文件
        scanner = FileScanner(source_dir)
        java_files = scanner.scan_java()  # 使用 scan_java() 方法扫描所有 .java 文件
        
        if not java_files:
            return Result.fail(f"No Java files found in {source_dir}")
        
        # 3. 清理注释并保存
        processed = []
        for file_info in java_files:
            # 读取原始文件内容
            with open(file_info.path, 'r', encoding='utf-8') as f:
                original = f.read()
            
            # 移除所有注释（包括 Javadoc、单行、多行注释）
            cleaned = JavaCommentRemover.remove(original)
            
            # 输出到 clean 目录（保持原始目录结构）
            # 例如：source/com/example/Main.java -> clean/com/example/Main.java
            output_path = FileScanner.ensure_output_path(
                file_info.path, source_dir, clean_dir
            )
            
            # 写入清理后的代码
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            # 记录处理信息
            processed.append({
                "original": str(file_info.path),
                "cleaned": str(output_path),
                "original_lines": file_info.lines,
                "cleaned_lines": len(cleaned.splitlines())
            })
        
        # 4. 存储结果到 ctx，供后续命令（如 GenerateCommand）使用
        ctx.set("work_dir", str(work_dir))
        ctx.set("source_name", source_name)
        ctx.set("source_dir", str(source_dir))
        ctx.set("clean_dir", str(clean_dir))
        ctx.set("processed_files", processed)
        
        # 计算统计信息
        total_original_lines = sum(f["original_lines"] for f in processed)
        total_cleaned_lines = sum(f["cleaned_lines"] for f in processed)
        removed_lines = total_original_lines - total_cleaned_lines
        
        return Result.ok(
            data={
                "source_name": source_name,                          # 项目名称
                "source_dir": str(source_dir),                       # 原始代码副本目录
                "clean_dir": str(clean_dir),                         # 清理后代码目录
                "file_count": len(processed),                        # 处理的文件数
                "total_original_lines": total_original_lines,        # 原始代码总行数
                "total_cleaned_lines": total_cleaned_lines           # 清理后代码总行数
            },
            message=f"Cleaned {len(processed)} Java files (removed {removed_lines} comment lines)"
        )