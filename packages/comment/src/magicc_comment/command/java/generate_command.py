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
    """
    
    def __init__(self):
        super().__init__()
        self.progress_display = ProgressDisplay()
        self.template_loader = PromptTemplateLoader()
    
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
    
    def _extract_methods_from_code(self, content: str) -> List[Dict]:
        """从Java代码中提取所有方法签名"""
        methods = []
        pattern = re.compile(
            r'^(?!.*\/\*|\*\/)(public|protected|private)?\s*'
            r'([\w\<\>\[\]]+)\s+'
            r'(\w+)\s*\('
            r'([^)]*)'
            r'\)\s*'
            r'(throws\s+[\w\s,]+)?\s*\{?',
            re.MULTILINE
        )
        
        for match in pattern.finditer(content):
            full_match = match.group(0)
            if full_match.rstrip().endswith(';'):  # 跳过接口方法
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
        """使用模板构建prompt"""
        return template.format(method_signature=method_signature)
    
    def _extract_comment(self, response: str) -> str:
        """从LLM响应中提取JavaDoc注释"""
        if response and '/**' in response and '*/' in response:
            start = response.find('/**')
            end = response.find('*/', start) + 2
            return response[start:end]
        return response
    
    def _get_file_stem(self, file_info) -> str:
        """获取文件名的stem（不含扩展名）"""
        # FileInfo 对象可能有不同的属性名
        if hasattr(file_info, 'stem'):
            return file_info.stem
        elif hasattr(file_info, 'name'):
            # 从文件名提取stem
            return Path(file_info.name).stem
        elif hasattr(file_info, 'path'):
            return Path(file_info.path).stem
        else:
            # 最后尝试：将对象转为字符串处理
            return str(file_info).split('.')[0]
    
    def _get_file_name(self, file_info) -> str:
        """获取文件名"""
        if hasattr(file_info, 'name'):
            return file_info.name
        elif hasattr(file_info, 'path'):
            return Path(file_info.path).name
        else:
            return str(file_info)
    
    def execute(self, ctx: Context) -> Result:
        # 初始化任务信息
        if task_info := ctx.get("current_task"):
            self.set_task_info(task_info)
        
        # 获取 LLM 客户端
        llm_client = self.get_llm_client()
        if not llm_client:
            return Result.fail("LLM client not injected")
        
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
        
        # 输出目录
        _model_name = self.get_model_name()
        output_dir = Path(ctx.get( work_dir / source_name / "output" / 
                                  (_model_name or "default").replace(":", "_")))
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
                # 获取文件路径
                if hasattr(file_info, 'path'):
                    file_path = Path(file_info.path)
                else:
                    # 如果 FileInfo 对象可能直接是 Path 或字符串
                    file_path = Path(str(file_info))
                
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取方法
                methods = self._extract_methods_from_code(content)
                file_name = self._get_file_name(file_info)
                
                if not methods:
                    self._print_progress(file_idx, total_files, 0, 0, file_name, 
                                       success=True, error_msg="No methods found", 
                                       is_last=(file_idx == total_files))
                    continue
                
                # 为每个方法生成注释
                method_results = []
                total_methods = len(methods)
                
                for method_idx, method in enumerate(methods, 1):
                    # 更新进度（开始处理）
                    self._print_progress(file_idx, total_files, method_idx-1, total_methods,
                                       f"{file_name}::{method['method_name']}")
                    
                    # 生成注释
                    prompt = self._build_prompt(method['signature'], prompt_template)
                    response = llm_client.generate(prompt)
                    comment = self._extract_comment(response)
                    
                    method_results.append({
                        'method_name': method['method_name'],
                        'original_signature': method['signature'],
                        'generated_comment': comment or "【生成失败】",
                        'line_number': method['line_number'],
                        'success': bool(comment)
                    })
                    
                    # 完成进度
                    self._print_progress(file_idx, total_files, method_idx, total_methods,
                                       f"{file_name}::{method['method_name']}",
                                       success=bool(comment), error_msg=None if comment else "生成失败",
                                       is_last=(file_idx == total_files and method_idx == total_methods))
                    
                    time.sleep(0.5)  # 避免请求过快
                
                # 保存结果
                file_result = {
                    'file': file_name,
                    'path': str(file_path),
                    'methods': method_results,
                    'total': len(methods),
                    'success_count': sum(1 for m in method_results if m['success'])
                }
                all_results.append(file_result)
                
                # 输出JSON - 修复这里：使用 file_path.stem
                json_file = output_dir / f"{file_path.stem}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(file_result, f, ensure_ascii=False, indent=2)
                    
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
        
        ctx.set("comment_dir", str(output_dir))
        ctx.set("comments", all_results)
        if model_name := self.get_model_name():
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