# packages/comment/src/magicc_comment/command/prompt_command.py
from pathlib import Path
from magicc_shared.core import Command, Context, Result
from magicc_shared.utils import FileScanner


class PromptCommand(Command):
    """为每个 Java 文件生成 prompt"""
    
    def execute(self, ctx: Context) -> Result:
        work_dir = ctx.get("work_dir")
        source_name = ctx.get("source_name")
        
        if not work_dir or not source_name:
            return Result.fail("work_dir and source_name are required")
        
        work_dir = Path(work_dir)
        clean_dir = work_dir / source_name / "clean"
        prompt_dir = work_dir / source_name / "prompt"
        
        if not clean_dir.exists():
            return Result.fail(f"Clean directory not found: {clean_dir}")
        
        # 扫描所有 Java 文件
        scanner = FileScanner(clean_dir)
        java_files = scanner.scan_java()
        
        if not java_files:
            return Result.fail(f"No Java files found in {clean_dir}")
        
        # 创建 prompt 目录
        prompt_dir.mkdir(parents=True, exist_ok=True)
        
        prompts = []
        for file_info in java_files:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # 构建 prompt
            prompt = self._build_prompt(code, file_info.name)
            
            # 生成输出路径（保持目录结构，扩展名改为 .prompt）
            relative_path = file_info.path.relative_to(clean_dir)
            prompt_path = prompt_dir / relative_path.with_suffix(".prompt")
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            prompts.append({
                "source": str(file_info.path),
                "prompt": str(prompt_path),
                "line_count": len(code.splitlines())
            })
        
        # 存储结果到 ctx
        ctx.set("prompt_dir", str(prompt_dir))
        ctx.set("prompts", prompts)
        
        return Result.ok(
            data={
                "prompt_count": len(prompts),
                "prompt_dir": str(prompt_dir),
                "total_lines": sum(p["line_count"] for p in prompts)
            },
            message=f"Generated {len(prompts)} prompts"
        )
    
    def _build_prompt(self, code: str, filename: str) -> str:
        """构建 LLM 提示词"""
        # 限制代码长度，避免 token 超限
        max_code_length = 2000
        if len(code) > max_code_length:
            code = code[:max_code_length] + "\n// ... (truncated)"
        
        # 使用转义或字符串拼接避免三引号问题
        prompt_template = (
            "You are a Java code documentation expert.\n\n"
            "Task: Generate a concise Javadoc comment for the following Java code.\n\n"
            "Requirements:\n"
            "- Use Javadoc format (/** ... */)\n"
            "- Include @param for each parameter (if method)\n"
            "- Include @return if method returns value\n"
            "- Include @throws if method throws exceptions\n"
            "- Keep description under 3 sentences\n"
            "- Do NOT include the code itself in your response\n"
            "- Output ONLY the Javadoc comment, no explanation\n\n"
            f"Java file: {filename}\n\n"
            "```java\n"
            f"{code}\n"
            "```\n\n"
            "Javadoc comment:"
        )
        return prompt_template