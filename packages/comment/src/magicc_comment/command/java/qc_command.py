# packages/comment/src/magicc_comment/command/qc_command.py
from magicc_shared.core import Command, Context, Result


class QCCommand(Command):
    """质量检查命令"""
    
    def execute(self, ctx: Context) -> Result:
        comments = ctx.get("comments", [])
        
        if not comments:
            return Result.fail("No comments to check")
        
        # 简单质量检查：长度、格式
        passed = []
        failed = []
        
        for comment in comments:
            content = comment.get("comment", "")
            if len(content) < 10:
                failed.append(comment)
            elif not content.startswith("/**"):
                failed.append(comment)
            else:
                passed.append(comment)
        
        ctx.set("qc_passed", passed)
        ctx.set("qc_failed", failed)
        
        return Result.ok(
            data={"passed": len(passed), "failed": len(failed)},
            message=f"QC: {len(passed)} passed, {len(failed)} failed"
        )