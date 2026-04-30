# magicc_comment/command/container.py - 改进版本
from .java.clean_command import CleanCommand
from .java.prompt_command import PromptCommand
from .java.generate_command import GenerateCommand
from .java.qc_command import QCCommand
from .java.report_command import ReportCommand
from .java.compare_report_command import CompareReportCommand
from magicc_shared.container import register_command


def _regist_java_command():    
    """
    注册 Java 语言的所有命令
    
    该函数将 Java 相关的命令类注册到全局命令容器中，使得 pipeline 可以通过
    命令名称（如 "clean", "generate" 等）来查找和执行对应的命令。
    
    注册的命令包括：
        - clean: 清理命令，用于清理临时文件或缓存
        - prompt: 提示词命令，用于生成或处理提示词
        - generate: 生成命令，用于生成代码注释
        - qc: 质量控制命令，用于检查和验证注释质量
        - report: 报告命令，用于生成统计报告
        - compare: 比较报告命令，用于对比不同版本的报告
    
    Note:
        该函数使用 magicc_shared.container.register_command 进行注册，
        注册格式为 register_command(language, command_name, command_class)
    """
    register_command("java", "clean", CleanCommand)
    register_command("java", "prompt", PromptCommand)
    register_command("java", "generate", GenerateCommand)
    register_command("java", "qc", QCCommand)
    register_command("java", "report", ReportCommand)
    register_command("java", "compare", CompareReportCommand)


# 语言注册映射
# 该字典定义了支持的语言类型及其对应的注册函数
# 键为语言名称（字符串），值为该语言的命令注册函数
# 通过这种映射方式，可以方便地扩展支持新的编程语言
_LANGUAGE_REGISTRARS = {
    "java": _regist_java_command,
    # "python": _regist_python_command,  # 未来扩展
    # "go": _regist_go_command,
}

def regist_command(types: str):
    """
    通用命令注册入口
    
    根据指定的语言类型，调用对应的注册函数来注册该语言所有相关的命令。
    这是外部调用注册命令的统一接口，封装了具体语言的注册细节。
    
    Args:
        types: 语言类型，支持的值包括：
               - "java": Java 语言
               - "python": Python 语言（未来扩展）
               - "go": Go 语言（未来扩展）
               - "rust": Rust 语言（未来扩展）
    
    Example:
        >>> # 注册 Java 语言的所有命令
        >>> regist_command("java")
        ✅ 已注册 java 语言的所有命令
        
        >>> # 尝试注册不支持的语言
        >>> regist_command("ruby")
        ⚠️ 不支持的语言类型: ruby
    
    Note:
        如果指定的语言类型不在 _LANGUAGE_REGISTRARS 映射中，
        函数会输出警告信息但不会抛出异常，保证系统的健壮性。
        如需支持新的语言，需要在 _LANGUAGE_REGISTRARS 中添加对应的映射关系。
    """
    registrar = _LANGUAGE_REGISTRARS.get(types)
    if registrar:
        registrar()
        print(f"✅ 已注册 {types} 语言的所有命令")
    else:
        print(f"⚠️ 不支持的语言类型: {types}")