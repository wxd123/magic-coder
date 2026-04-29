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


def find_config_files(config_path):
    """
    在指定路径下自动查找配置文件
    
    Args:
        config_path: 配置目录路径
    
    Returns:
        tuple: (pipeline_config_path, prompt_config_path)
    """
    config_dir = Path(config_path)
    
    if not config_dir.exists():
        return None, None
    
    # 查找 pipeline 配置文件
    pipeline_config = None
    for pattern in ["pipeline.yaml", "pipeline.yml", "config.yaml", "config.yml"]:
        candidate = config_dir / pattern
        if candidate.exists():
            pipeline_config = candidate
            break
    
    # 查找 prompt 模板文件
    prompt_config = None
    for pattern in ["prompt.txt", "prompt.md", "template.txt", "template.md"]:
        candidate = config_dir / pattern
        if candidate.exists():
            prompt_config = candidate
            break
    
    return pipeline_config, prompt_config


def main():
    parser = argparse.ArgumentParser(
        description="Magic Comment - 代码注释生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用配置文件目录（自动查找 pipeline.yaml 和 prompt.txt）
  magic-comment --config-path ./my_config --source /path/to/project

  # 手动指定 pipeline 配置文件
  magic-comment --pipeline config/pipeline.yaml --source /path/to/project

  # 运行指定的 Pipeline 名称
  magic-comment --pipeline config/pipeline.yaml --name comparison_pipeline --source /path/to/project

  # 使用自定义 prompt 模板
  magic-comment --pipeline config/pipeline.yaml --source /path/to/project --prompt-config config/my_prompt.txt

  # 只清理注释
  magic-comment --clean --source /path/to/project

  # 组合使用：配置文件目录 + 指定 pipeline 名称
  magic-comment --config-path ./my_config --name custom_pipeline --source /path/to/project
        """
    )
    
    # 配置参数组
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument("--config-path", "-c", help="配置文件目录路径（自动查找 pipeline.yaml 和 prompt.txt）")
    config_group.add_argument("--pipeline", "-p", help="Pipeline 配置文件路径（手动指定）")
    
    parser.add_argument("--name", "-n", default="pipeline", help="Pipeline 名称（默认 pipeline）")
    parser.add_argument("--source", "-s", required=True, help="源代码路径")
    parser.add_argument("--work-dir", "-w", default=str(Path.home() / "magic_coder" / "magic_comment"),
                        help="工作目录（默认 ~/magic_coder/magic_comment）")
    parser.add_argument("--prompt-config", "-pc", help="Prompt 模板配置文件路径（用于 generate 命令）")
    parser.add_argument("--clean", action="store_true", help="仅清理注释")
    
    args = parser.parse_args()
    
    # 处理 --config-path 参数
    if args.config_path:
        pipeline_config, prompt_config = find_config_files(args.config_path)
        
        if not pipeline_config:
            print(f"❌ 在 {args.config_path} 中未找到 pipeline 配置文件（pipeline.yaml/config.yaml）")
            sys.exit(1)
        
        # 覆盖参数
        args.pipeline = str(pipeline_config)
        if prompt_config and not args.prompt_config:
            args.prompt_config = str(prompt_config)
            print(f"🔍 自动发现 prompt 模板: {prompt_config}")
        
        print(f"🔍 自动发现 pipeline 配置: {pipeline_config}")
    
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
    
    # 设置 prompt 配置文件路径（如果提供）
    if args.prompt_config:
        prompt_config_path = Path(args.prompt_config)
        if not prompt_config_path.exists():
            print(f"⚠️  Prompt 配置文件不存在: {prompt_config_path}，将使用默认模板")
        else:
            ctx.set("prompt_config_path", str(prompt_config_path))
            print(f"📝 Prompt 模板: {prompt_config_path}")
    
    # 如果使用 config-path，也传递配置目录信息
    if hasattr(args, 'config_path') and args.config_path:
        ctx.set("config_dir", str(Path(args.config_path).absolute()))
    
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