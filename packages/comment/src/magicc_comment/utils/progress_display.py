# packages/comment/src/magicc_comment/utils/progress_display.py
from typing import Optional, Dict, Any


class ProgressDisplay:
    """通用的进度显示类"""
    
    def __init__(self):
        self.current_task: Optional[Dict[str, Any]] = None
    
    def set_task(self, task_info: Dict[str, Any]):
        """设置当前任务信息"""
        self.current_task = task_info
    
    def update_progress(self, current_file: int, total_files: int,
                        current_func: int, total_funcs: int,
                        filename: str, success: bool = True, 
                        error_msg: str = None, is_last: bool = False):
        """更新进度显示"""
        
        if not self.current_task:
            # 没有任务信息，使用简单显示
            self._print_simple_progress(current_file, total_files, current_func, 
                                       total_funcs, filename, success, error_msg, is_last)
            return
        
        # 构建任务栏（固定宽度20）
        command = self.current_task.get("command", "unknown")
        # 解析命令名称
        if ":" in command:
            cmd_name = command.split(":")[-1]
        else:
            cmd_name = command
        
        # 添加模型信息（如果是 generate 命令）
        models = self.current_task.get("models", [])
        if models:
            model_display = f"[{models[0][:8]}]" if models else ""
            task_display = f"{cmd_name}{model_display}"
        else:
            task_display = cmd_name
        
        task_col = f"{task_display:<20}"
        
        # 构建文件名栏（固定宽度35）
        display_filename = filename if len(filename) <= 33 else filename[:30] + "..."
        filename_col = f"{display_filename:<35}"
        
        # 构建进度栏
        progress_col = f"函数({current_func:>3}/{total_funcs:<3}) 文件({current_file:>3}/{total_files:<3})"
        
        # 构建状态栏
        if success:
            status_col = "✅"
        else:
            error_display = f" {error_msg[:15]}" if error_msg else ""
            status_col = f"❌{error_display}"
        
        # 组合输出
        output = f"\r{task_col} {filename_col} {progress_col} {status_col}"
        
        if is_last:
            print(output)
        else:
            print(output, end='', flush=True)
    
    def _print_simple_progress(self, current_file: int, total_files: int,
                               current_func: int, total_funcs: int,
                               filename: str, success: bool = True, 
                               error_msg: str = None, is_last: bool = False):
        """简单进度显示（无任务信息）"""
        display_filename = filename if len(filename) <= 33 else filename[:30] + "..."
        first_col = f"{display_filename:<35}"
        second_col = f"函数({current_func:>3}/{total_funcs:<3})"
        
        if success:
            status = "✅"
            third_col = f"文件({current_file:>3}/{total_files:<3}) {status}"
        else:
            status = "❌"
            error_display = f" {error_msg[:15]}" if error_msg else ""
            third_col = f"文件({current_file:>3}/{total_files:<3}) {status}{error_display}"
        
        output = f"\r{first_col} {second_col} {third_col}"
        
        if is_last:
            print(output)
        else:
            print(output, end='', flush=True)