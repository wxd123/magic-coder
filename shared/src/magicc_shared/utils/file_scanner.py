# shared/src/magicc_shared/utils/file_scanner.py
from pathlib import Path
from typing import List, Optional, Set, Callable
from dataclasses import dataclass


@dataclass
class FileInfo:
    """文件信息"""
    path: Path           # 完整路径
    relative_path: Path  # 相对于根目录的路径
    name: str            # 文件名
    suffix: str          # 扩展名（如 .java）
    size: int            # 文件大小（字节）
    lines: int           # 行数


class FileScanner:
    """文件扫描器 - 递归查找指定扩展名的文件"""
    
    def __init__(self, root_dir: Path):
        """
        初始化扫描器
        
        Args:
            root_dir: 根目录
        """
        self.root_dir = Path(root_dir)
        
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.root_dir}")
    
    def scan(self, extensions: Set[str]) -> List[FileInfo]:
        """
        扫描目录，返回所有扩展名匹配的文件
        
        Args:
            extensions: 扩展名集合，如 {".java", ".py"}
            
        Returns:
            FileInfo 列表
        """
        files = []
        
        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix in extensions:
                files.append(self._to_file_info(file_path))
        
        return files
    
    def scan_java(self) -> List[FileInfo]:
        """扫描所有 Java 文件"""
        return self.scan({".java"})
    
    def scan_python(self) -> List[FileInfo]:
        """扫描所有 Python 文件"""
        return self.scan({".py"})
    
    def scan_by_pattern(self, pattern: str) -> List[FileInfo]:
        """
        按 glob 模式扫描
        
        Args:
            pattern: glob 模式，如 "*.java" 或 "src/**/*.java"
        """
        files = []
        for file_path in self.root_dir.glob(pattern):
            if file_path.is_file():
                files.append(self._to_file_info(file_path))
        return files
    
    def for_each(self, extensions: Set[str], callback: Callable[[FileInfo], None]) -> int:
        """
        遍历每个匹配的文件并执行回调
        
        Args:
            extensions: 扩展名集合
            callback: 回调函数，接收 FileInfo 参数
            
        Returns:
            处理文件数量
        """
        files = self.scan(extensions)
        for file_info in files:
            callback(file_info)
        return len(files)
    
    def for_each_java(self, callback: Callable[[FileInfo], None]) -> int:
        """遍历每个 Java 文件并执行回调"""
        return self.for_each({".java"}, callback)
    
    def _to_file_info(self, file_path: Path) -> FileInfo:
        """转换为 FileInfo 对象"""
        return FileInfo(
            path=file_path,
            relative_path=file_path.relative_to(self.root_dir),
            name=file_path.name,
            suffix=file_path.suffix,
            size=file_path.stat().st_size,
            lines=self._count_lines(file_path)
        )
    
    def _count_lines(self, file_path: Path) -> int:
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except (UnicodeDecodeError, IOError):
            return 0
    
    @staticmethod
    def ensure_output_path(input_file: Path, input_root: Path, output_root: Path) -> Path:
        """
        保持目录结构，生成输出路径
        
        Args:
            input_file: 输入文件路径
            input_root: 输入根目录
            output_root: 输出根目录
            
        Returns:
            输出文件路径
        """
        relative_path = input_file.relative_to(input_root)
        output_path = Path(output_root) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path