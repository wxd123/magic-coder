# packages/comment/src/magicc_comment/command/generate_command.py

import re
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from magicc_shared.core import LLMCommand, Context, Result
from magicc_shared.utils import FileScanner
from magicc_comment.utils.progress_display import ProgressDisplay
from magicc_comment.utils.prompt_template_loader import PromptTemplateLoader


class GenerateCommand(LLMCommand):
    """
    生成注释命令
    
    功能：为Java代码中的方法生成标准的JavaDoc注释
    
    该类继承自 LLMCommand，利用大语言模型为 Java 源代码中的方法自动生成
    符合规范的 JavaDoc 注释。支持批量处理多个 Java 文件，并为每个方法
    生成独立的注释，结果以 JSON 格式保存。
    
    主要特性：
        - 自动识别 Java 方法签名（包括访问修饰符、返回类型、参数等）
        - 跳过接口方法（以分号结尾的方法声明）
        - 使用模板构建请求提示词
        - 支持进度显示和错误处理
        - 保持目录结构的输出方式
        - 支持请求间隔控制，避免 API 限流
    
    使用示例：
        command = GenerateCommand()
        command.set_llm_manager(llm_manager, "gpt-4")
        result = command.execute(context)
    """
    
    # 正则表达式缓存
    # 用于匹配 Java 方法签名的正则表达式
    # 匹配模式：可选的访问修饰符 + 返回类型 + 方法名 + 参数列表 + 可选的 throws 子句 + 可选的大括号
    METHOD_PATTERN = re.compile(
        r'^(?!.*\/\*|\*\/)(public|protected|private)?\s*'
        r'([\w\<\>\[\]]+)\s+'
        r'(\w+)\s*\('
        r'([^)]*)'
        r'\)\s*'
        r'(throws\s+[\w\s,]+)?\s*\{?',
        re.MULTILINE
    )
    
    def __init__(self):
        """初始化生成命令实例"""
        super().__init__()
        self.progress_display = ProgressDisplay()  # 进度显示工具
        self.template_loader = PromptTemplateLoader()  # 提示词模板加载器
        self.request_interval = 0.5  # 请求间隔（秒），可配置以避免 API 限流
    
    def _print_progress(self, current_file: int, total_files: int, 
                       current_func: int, total_funcs: int,
                       filename: str, success: bool = True, error_msg: str = None,
                       is_last: bool = False):
        """
        打印进度信息（委托给 ProgressDisplay）
        
        Args:
            current_file: 当前处理的文件序号
            total_files: 总文件数
            current_func: 当前处理的方法序号
            total_funcs: 当前文件的总方法数
            filename: 当前处理的文件名
            success: 当前操作是否成功
            error_msg: 错误信息（当 success=False 时）
            is_last: 是否为最后一个操作（用于控制输出格式）
        """
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
        """
        设置任务信息（由 executor 调用）
        
        Args:
            task_info: 任务信息字典，包含命令名称、模型列表、描述等
        """
        self.progress_display.set_task(task_info)
    
    def _extract_methods_from_code(self, content: str) -> List[Dict]:
        """
        从Java代码中提取所有方法签名
        
        Args:
            content: Java 源代码内容
            
        Returns:
            List[Dict]: 方法信息列表，每个元素包含：
                - signature: 方法签名（完整字符串）
                - method_name: 方法名称
                - line_number: 方法所在行号
                - return_type: 返回类型
            
        Note:
            会自动跳过以分号结尾的接口方法声明
        """
        methods = []
        
        for match in self.METHOD_PATTERN.finditer(content):
            full_match = match.group(0)
            # 跳过接口方法（以分号结尾的方法声明）
            if full_match.rstrip().endswith(';'):
                continue
                
            line_num = content[:match.start()].count('\n') + 1
            methods.append({
                'signature': full_match.strip(),
                'method_name': match.group(3),
                'line_number': line_num,
                'return_type': match.group(2)
            })
        
        return methods
    
    def _build_prompt(self, method_signature: str, template: str) -> str:
        """
        使用模板构建prompt
        
        Args:
            method_signature: 方法签名
            template: 提示词模板，应包含 {method_signature} 占位符
            
        Returns:
            str: 构建完成的提示词
        """
        return template.format(method_signature=method_signature)
    
    def _extract_comment(self, response: str) -> str:
        """
        从LLM响应中提取JavaDoc注释
        
        Args:
            response: LLM 返回的原始响应文本
            
        Returns:
            str: 提取出的 JavaDoc 注释，如果找不到则返回原响应
            
        Note:
            通过查找 '/**' 和 '*/' 标记来提取注释块
        """
        if response and '/**' in response and '*/' in response:
            start = response.find('/**')
            end = response.find('*/', start) + 2
            return response[start:end]
        return response
    
    def _get_file_name(self, file_info) -> str:
        """
        获取文件名
        
        Args:
            file_info: 文件信息对象（可能包含 name 或 path 属性，也可能是字符串）
            
        Returns:
            str: 文件名
        """
        if hasattr(file_info, 'name'):
            return file_info.name
        elif hasattr(file_info, 'path'):
            return Path(file_info.path).name
        else:
            return str(file_info)
    
    def _get_file_path(self, file_info) -> Path:
        """
        获取文件路径
        
        Args:
            file_info: 文件信息对象（可能包含 path 属性，也可能是字符串）
            
        Returns:
            Path: 文件路径对象
        """
        if hasattr(file_info, 'path'):
            return Path(file_info.path)
        return Path(str(file_info))
    
    def _get_output_path(self, file_path: Path, cleaned_dir: Path, output_dir: Path) -> Path:
        """
        获取输出文件路径，保持目录结构
        
        Args:
            file_path: 源文件路径
            cleaned_dir: 清理后的源目录（基准目录）
            output_dir: 输出根目录
        
        Returns:
            Path: 完整的输出文件路径，保持与源文件相同的相对目录结构
            
        Example:
            如果 cleaned_dir = /project/src, file_path = /project/src/com/example/Main.java,
            output_dir = /project/output, 则返回 /project/output/com/example/Main.json
        """
        # 获取相对于 cleaned_dir 的相对路径
        try:
            relative_path = file_path.relative_to(cleaned_dir)
        except ValueError:
            # 如果不在 cleaned_dir 下，使用文件名
            return output_dir / f"{file_path.stem}.json"
        
        # 替换扩展名为 .json
        output_path = output_dir / relative_path.with_suffix('.json')
        
        # 确保父目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
    def _process_single_file(self, file_info, cleaned_dir: Path, output_dir: Path, 
                              prompt_template: str, file_idx: int, total_files: int) -> Optional[Dict]:
        """
        处理单个文件
        
        Args:
            file_info: 文件信息对象
            cleaned_dir: 清理后的源目录
            output_dir: 输出根目录
            prompt_template: 提示词模板
            file_idx: 当前文件序号（从1开始）
            total_files: 总文件数
            
        Returns:
            Optional[Dict]: 文件处理结果字典，包含文件信息和方法注释结果；
                           如果文件没有方法，返回 None
            
        Note:
            处理流程：
            1. 读取文件内容
            2. 提取所有方法签名
            3. 为每个方法生成注释
            4. 保存结果到 JSON 文件
        """
        file_path = self._get_file_path(file_info)
        file_name = self._get_file_name(file_info)
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取方法
        methods = self._extract_methods_from_code(content)
        
        if not methods:
            self._print_progress(file_idx, total_files, 0, 0, file_name, 
                               success=True, error_msg="No methods found", 
                               is_last=(file_idx == total_files))
            return None
        
        # 为每个方法生成注释
        method_results = []
        total_methods = len(methods)
        
        for method_idx, method in enumerate(methods, 1):
            self._print_progress(file_idx, total_files, method_idx-1, total_methods,
                               f"{file_name}::{method['method_name']}")
            
            prompt = self._build_prompt(method['signature'], prompt_template)
            
            # 使用统一的 generate 方法（继承自 LLMCommand）
            response = self.generate(prompt)
            comment = self._extract_comment(response)
            
            method_results.append({
                'method_name': method['method_name'],
                'original_signature': method['signature'],
                'generated_comment': comment or "【生成失败】",
                'line_number': method['line_number'],
                'success': bool(comment)
            })
            
            self._print_progress(file_idx, total_files, method_idx, total_methods,
                               f"{file_name}::{method['method_name']}",
                               success=bool(comment), error_msg=None if comment else "生成失败",
                               is_last=(file_idx == total_files and method_idx == total_methods))
            
            # 等待一段时间，避免请求过于频繁
            time.sleep(self.request_interval)
        
        # 获取输出路径（保持目录结构）
        output_path = self._get_output_path(file_path, cleaned_dir, output_dir)
        
        # 保存结果
        file_result = {
            'file': file_name,
            'path': str(file_path),
            'relative_path': str(file_path.relative_to(cleaned_dir)) if file_path.is_relative_to(cleaned_dir) else file_name,
            'methods': method_results,
            'total': len(methods),
            'success_count': sum(1 for m in method_results if m['success'])
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(file_result, f, ensure_ascii=False, indent=2)
        
        return file_result
    
    def execute(self, ctx: Context) -> Result:
        """
        执行生成注释命令
        
        Args:
            ctx: 执行上下文，需要包含以下键值：
                - current_task: 当前任务信息（可选）
                - work_dir: 工作目录
                - source_name: 源代码名称
                - cleaned_dir: 清理后的代码目录（可选，默认为 work_dir/source_name/clean）
                - prompt_config_path: 提示词配置文件路径
                
        Returns:
            Result: 执行结果对象
                - 成功时：data 包含文件数、方法数、成功数、成功率、输出目录等信息
                - 失败时：message 包含错误信息
                
        Note:
            执行流程：
            1. 验证 LLM 管理器已注入
            2. 加载提示词模板
            3. 准备输入输出目录
            4. 扫描 Java 文件
            5. 批量处理文件生成注释
            6. 统计结果并返回
            
            输出目录结构：
                work_dir/source_name/output/{model_name}/{相对路径}/{文件名}.json
        """
        # 初始化任务信息
        if task_info := ctx.get("current_task"):
            self.set_task_info(task_info)
        
        # 检查 LLM 管理器是否已注入
        if not self.get_llm_manager():
            return Result.fail("LLM manager not injected")
        
        # 加载 prompt 模板
        prompt_config_path = ctx.get("prompt_config_path")
        prompt_template = self.template_loader.load_template(prompt_config_path)
        
        # 准备目录
        work_dir = Path(ctx.get("work_dir", ""))
        source_name = ctx.get("source_name", "")
        if not work_dir or not source_name:
            return Result.fail("work_dir and source_name are required")
        
        # 输入目录：clean
        cleaned_dir = Path(ctx.get("cleaned_dir", work_dir / source_name / "clean"))
        if not cleaned_dir.exists():
            return Result.fail(f"Cleaned directory not found: {cleaned_dir}")
        
        # 输出目录：按模型名称组织，避免不同模型的结果相互覆盖
        model_name = self.get_model_name()
        output_dir = work_dir / source_name / "output" / (model_name or "default").replace(":", "_")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描Java文件
        java_files = FileScanner(cleaned_dir).scan({".java"})
        if not java_files:
            return Result.fail(f"No Java files found in {cleaned_dir}")
        
        # 处理所有文件
        all_results = []
        total_files = len(java_files)
        
        for file_idx, file_info in enumerate(java_files, 1):
            try:
                file_result = self._process_single_file(
                    file_info, cleaned_dir, output_dir, prompt_template,
                    file_idx, total_files
                )
                if file_result:
                    all_results.append(file_result)
                    
            except Exception as e:
                file_name = self._get_file_name(file_info)
                self._print_progress(file_idx, total_files, 0, 1, file_name,
                                   success=False, error_msg=str(e)[:30],
                                   is_last=(file_idx == total_files))
                return Result.fail(f"Failed to process {file_name}: {e}")
        
        # 统计并返回
        total_methods = sum(r['total'] for r in all_results)
        total_success = sum(r['success_count'] for r in all_results)
        success_rate = (total_success / total_methods * 100) if total_methods > 0 else 0
        
        # 将结果保存到上下文中，供后续命令使用
        ctx.set("comment_dir", str(output_dir))
        ctx.set("comments", all_results)
        if model_name:
            ctx.set(f"comments_{model_name}", all_results)
        
        return Result.ok(
            data={
                "file_count": len(all_results),
                "method_count": total_methods,
                "success_count": total_success,
                "success_rate": success_rate,
                "comment_dir": str(output_dir)
            },
            message=f"Generated {total_success}/{total_methods} comments ({success_rate:.1f}%)"
        )