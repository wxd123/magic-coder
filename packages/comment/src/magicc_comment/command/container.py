# magicc_comment/command/container.py - 改进版本
from .java.clean_command import CleanCommand
from .java.prompt_command import PromptCommand
from .java.generate_command import GenerateCommand
from .java.qc_command import QCCommand
from .java.report_command import ReportCommand
from .java.compare_report_command import CompareReportCommand
from magicc_shared.container import register_command


def _regist_java_command():    
    """注册 Java 命令"""
    register_command("java", "clean", CleanCommand)
    register_command("java", "prompt", PromptCommand)
    register_command("java", "generate", GenerateCommand)
    register_command("java", "qc", QCCommand)
    register_command("java", "report", ReportCommand)
    register_command("java", "compare", CompareReportCommand)


# 语言注册映射
_LANGUAGE_REGISTRARS = {
    "java": _regist_java_command,
    # "python": _regist_python_command,  # 未来扩展
    # "go": _regist_go_command,
}

def regist_command(types: str):
    """
    通用命令注册入口
    
    Args:
        types: 语言类型 (java, python, go, rust)
    """
    registrar = _LANGUAGE_REGISTRARS.get(types)
    if registrar:
        registrar()
        print(f"✅ 已注册 {types} 语言的所有命令")
    else:
        print(f"⚠️ 不支持的语言类型: {types}")


