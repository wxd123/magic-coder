# packages/comment/src/magicc_comment/command/compare_report_command.py
from pathlib import Path
from magicc_shared.core import Command, Context, Result


class CompareReportCommand(Command):
    """生成模型对比报告"""
    
    def execute(self, ctx: Context) -> Result:
        results = ctx.get("_comparison_results", {})
        models = ctx.get("_comparison_models", [])
        work_dir = Path(ctx.get("work_dir"))
        source_name = ctx.get("source_name")
        
        if not results:
            return Result.fail("No comparison results found")
        
        report_dir = work_dir / source_name / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "comparison_report.md"
        
        report = f"# Model Comparison Report\n\n"
        report += f"## Project: {source_name}\n\n"
        report += f"| Model | Files | Output Directory |\n"
        report += f"|-------|-------|-----------------|\n"
        
        for model_name in models:
            result = results.get(model_name, {})
            file_count = result.get("comment_count", 0)
            comment_dir = result.get("comment_dir", "N/A")
            report += f"| {model_name} | {file_count} | `{comment_dir}` |\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return Result.ok(
            data={"report_path": str(report_path)},
            message=f"Comparison report saved to {report_path}"
        )