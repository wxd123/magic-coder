# packages/comment/src/magicc_comment/command/report_command.py
from pathlib import Path
from magicc_shared.core import Command, Context, Result


class ReportCommand(Command):
    """生成报告命令"""
    
    def execute(self, ctx: Context) -> Result:
        work_dir = Path(ctx.get("work_dir"))
        source_name = ctx.get("source_name")
        
        comments = ctx.get("comments", [])
        qc_passed = ctx.get("qc_passed", [])
        qc_failed = ctx.get("qc_failed", [])
        
        # 生成报告
        report_dir = work_dir / source_name / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "report.md"
        
        report = f"# Comment Generation Report\n\n"
        report += f"## Summary\n\n"
        report += f"- Total comments: {len(comments)}\n"
        report += f"- Passed QC: {len(qc_passed)}\n"
        report += f"- Failed QC: {len(qc_failed)}\n"
        
        if qc_failed:
            report += f"\n## Failed Items\n\n"
            for item in qc_failed[:10]:
                report += f"- {item.get('source', 'unknown')}\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        ctx.set("report_path", str(report_path))
        
        return Result.ok(
            data={"report_path": str(report_path)},
            message=f"Report saved to {report_path}"
        )