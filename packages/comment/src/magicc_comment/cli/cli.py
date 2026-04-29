# packages/comment/src/magicc_comment/cli/cli.py
#!/usr/bin/env python3
"""
Magic Comment - 代码注释生成工具
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "shared" / "src"))

from magicc_shared.core import Context
from magicc_comment.pipeline.executor import PipelineExecutor


def main():
    parser = argparse.ArgumentParser(
        description="Magic Comment - 代码注释生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行 Pipeline
  magic-comment --pipeline config/pipeline.yaml --source /path/to/project

  # 运行指定的 Pipeline 名称
  magic-comment --pipeline config/pipeline.yaml --name comparison_pipeline --source /path/to/project

  # 只清理注释
  magic-comment --clean --source /path/to/project
        """
    )
    
    parser.add_argument("--pipeline", "-p", help="Pipeline 配置文件路径")
    parser.add_argument("--name", "-n", default="pipeline", help="Pipeline 名称（默认 pipeline）")
    parser.add_argument("--source", "-s", required=True, help="源代码路径")
    parser.add_argument("--work-dir", "-w", default=str(Path.home() / "magic_coder" / "magic_comment"),
                        help="工作目录（默认 ~/magic_coder/magic_comment）")
    parser.add_argument("--clean", action="store_true", help="仅清理注释")
    
    args = parser.parse_args()
    
    if args.clean:
        cmd_clean(args)
    elif args.pipeline:
        cmd_run(args)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_run(args):
    """执行 Pipeline"""
    config_path = Path(args.pipeline)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        sys.exit(1)
    
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    executor = PipelineExecutor(config)
    
    ctx = Context()
    ctx.set("work_dir", args.work_dir)
    ctx.set("source_name", Path(args.source).name)
    ctx.set("source_path", args.source)
    
    print(f"📁 配置文件: {config_path}")
    print(f"📁 Pipeline: {args.name}")
    print(f"📁 源代码: {args.source}")
    print(f"📁 工作目录: {Path(args.work_dir) / Path(args.source).name}")
    print()
    
    result = executor.run(ctx, args.name)
    
    if result.success:
        print(f"\n✅ {result.message}")
        if result.data:
            for key, value in result.data.items():
                print(f"   {key}: {value}")
    else:
        print(f"\n❌ 失败: {result.message}")
        sys.exit(1)


def cmd_clean(args):
    """仅执行清理"""
    from magicc_comment.command.java.clean_command import CleanCommand
    
    source_path = Path(args.source)
    source_name = source_path.name
    work_dir = Path(args.work_dir)
    
    ctx = Context()
    ctx.set("work_dir", str(work_dir))
    ctx.set("source_name", source_name)
    ctx.set("source_path", str(source_path))
    
    print(f"📁 源代码: {source_path}")
    print(f"📁 工作目录: {work_dir / source_name}")
    print()
    
    cmd = CleanCommand()
    result = cmd.execute(ctx)
    
    if result.success:
        print(f"✅ {result.message}")
        print(f"   文件数: {result.data.get('file_count', 0)}")
        print(f"   输出: {result.data.get('clean_dir', 'N/A')}")
    else:
        print(f"❌ 失败: {result.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()