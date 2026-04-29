from magicc_comment.command.java.clean_command import CleanCommand
from magicc_comment.command.java.prompt_command import PromptCommand
from magicc_comment.command.java.generate_command import GenerateCommand
from magicc_comment.command.java.qc_command import QCCommand
from magicc_comment.command.java.report_command import ReportCommand
from magicc_shared.core import Context, Result

def run_java_pipeline(ctx: Context) -> Result:
    """Java 注释生成流水线"""
    commands = [
        CleanCommand(),
        PromptCommand(),
        GenerateCommand(),
        QCCommand(),
        ReportCommand()
    ]
    
    for cmd in commands:
        cmd.validate(ctx)
        result = cmd.execute(ctx)
        if not result.success:
            return result
    
    return Result.ok({"comment": ctx.get("comment")})