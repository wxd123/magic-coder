# shared/src/magicc_shared/utils/file_scanner.py
from pathlib import Path
from typing import List, Optional, Set, Callable
from dataclasses import dataclass


@dataclass
class FileInfo:
    """
    文件信息数据类，封装文件的基本属性和统计信息。
    
    用于在文件扫描和处理过程中传递文件的完整信息。
    
    属性:
        path: 文件的完整绝对路径
        relative_path: 相对于扫描根目录的路径，用于保持目录结构
        name: 文件名（包含扩展名）
        suffix: 文件扩展名（如 .java、.py、.go）
        size: 文件大小（字节数）
        lines: 文件行数（UTF-8 编码下统计，如果读取失败则为 0）
    
    示例:
        >>> info = FileInfo(
        ...     path=Path("/project/src/main.java"),
        ...     relative_path=Path("src/main.java"),
        ...     name="main.java",
        ...     suffix=".java",
        ...     size=1024,
        ...     lines=50
        ... )
        >>> print(f"{info.name}: {info.lines} lines")
        main.java: 50 lines
    """
    path: Path           # 完整路径
    relative_path: Path  # 相对于根目录的路径
    name: str            # 文件名
    suffix: str          # 扩展名（如 .java）
    size: int            # 文件大小（字节）
    lines: int           # 行数


class FileScanner:
    """
    文件扫描器 - 递归查找指定扩展名的文件。
    
    提供多种扫描方式：按扩展名集合扫描、按语言类型扫描、按 glob 模式扫描，
    以及遍历处理功能。支持统计文件行数并保持目录结构。
    
    设计用途:
        用于代码分析工具中扫描指定语言的源代码文件。
    
    示例:
        >>> scanner = FileScanner(Path("/path/to/project"))
        >>> # 扫描所有 Java 文件
        >>> java_files = scanner.scan_java()
        >>> for file_info in java_files:
        ...     print(f"{file_info.relative_path}: {file_info.lines} lines")
        
        >>> # 使用回调处理
        >>> def process(file_info: FileInfo):
        ...     print(f"Processing {file_info.name}")
        >>> scanner.for_each_java(process)
    """
    
    def __init__(self, root_dir: Path):
        """
        初始化扫描器。
        
        Args:
            root_dir: 扫描的根目录路径
        
        Raises:
            FileNotFoundError: 当 root_dir 不存在时抛出
        
        示例:
            >>> scanner = FileScanner(Path("./src"))
            >>> scanner = FileScanner(Path("/invalid/path"))  # 抛出 FileNotFoundError
        """
        self.root_dir = Path(root_dir)
        
        if not self.root_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.root_dir}")
    
    def scan(self, extensions: Set[str]) -> List[FileInfo]:
        """
        扫描目录，返回所有扩展名匹配的文件。
        
        递归遍历根目录下的所有文件，筛选出扩展名在指定集合中的文件。
        
        Args:
            extensions: 扩展名集合，如 {".java", ".py", ".go"}
        
        Returns:
            FileInfo 对象列表，按文件系统遍历顺序排列
        
        示例:
            >>> files = scanner.scan({".java", ".kt"})
            >>> for f in files:
            ...     print(f"{f.name}: {f.size} bytes")
        """
        files = []
        
        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix in extensions:
                files.append(self._to_file_info(file_path))
        
        return files
    
    def scan_java(self) -> List[FileInfo]:
        """
        扫描所有 Java 文件。
        
        Returns:
            Java 文件的 FileInfo 列表，扩展名为 .java
        
        示例:
            >>> java_files = scanner.scan_java()
            >>> print(f"Found {len(java_files)} Java files")
        """
        return self.scan({".java"})
    
    def scan_python(self) -> List[FileInfo]:
        """
        扫描所有 Python 文件。
        
        Returns:
            Python 文件的 FileInfo 列表，扩展名为 .py
        
        示例:
            >>> py_files = scanner.scan_python()
        """
        return self.scan({".py"})
    
    def scan_by_pattern(self, pattern: str) -> List[FileInfo]:
        """
        按 glob 模式扫描文件。
        
        提供更灵活的扫描方式，可以自定义匹配模式。
        
        Args:
            pattern: glob 模式，如 "*.java" 或 "src/**/*.java"
        
        Returns:
            匹配模式的文件 FileInfo 列表
        
        示例:
            >>> # 扫描所有 src 目录下的 Java 文件
            >>> files = scanner.scan_by_pattern("src/**/*.java")
            >>> # 扫描测试文件
            >>> test_files = scanner.scan_by_pattern("*Test.java")
        """
        files = []
        for file_path in self.root_dir.glob(pattern):
            if file_path.is_file():
                files.append(self._to_file_info(file_path))
        return files
    
    def for_each(self, extensions: Set[str], callback: Callable[[FileInfo], None]) -> int:
        """
        遍历每个匹配的文件并执行回调函数。
        
        适用于需要对每个文件执行操作的场景，如分析、转换等。
        
        Args:
            extensions: 扩展名集合
            callback: 回调函数，接收 FileInfo 参数，无返回值
        
        Returns:
            处理文件的总数量
        
        示例:
            >>> def count_lines(info: FileInfo):
            ...     print(f"{info.name}: {info.lines}")
            >>> total = scanner.for_each({".java", ".py"}, count_lines)
            >>> print(f"Processed {total} files")
        """
        files = self.scan(extensions)
        for file_info in files:
            callback(file_info)
        return len(files)
    
    def for_each_java(self, callback: Callable[[FileInfo], None]) -> int:
        """
        遍历每个 Java 文件并执行回调函数。
        
        Args:
            callback: 回调函数，接收 FileInfo 参数
        
        Returns:
            处理的 Java 文件数量
        
        示例:
            >>> def analyze_java(file_info: FileInfo):
            ...     # 分析 Java 文件
            ...     print(f"Analyzing {file_info.relative_path}")
            >>> count = scanner.for_each_java(analyze_java)
        """
        return self.for_each({".java"}, callback)
    
    def _to_file_info(self, file_path: Path) -> FileInfo:
        """
        将 Path 对象转换为 FileInfo 对象（内部方法）。
        
        提取文件的完整路径、相对路径、名称、扩展名、大小和行数。
        
        Args:
            file_path: 文件的完整路径
        
        Returns:
            包含文件完整信息的 FileInfo 对象
        """
        return FileInfo(
            path=file_path,
            relative_path=file_path.relative_to(self.root_dir),
            name=file_path.name,
            suffix=file_path.suffix,
            size=file_path.stat().st_size,
            lines=self._count_lines(file_path)
        )
    
    def _count_lines(self, file_path: Path) -> int:
        """
        统计文件行数（内部方法）。
        
        以 UTF-8 编码读取文件并统计行数。如果文件编码不是 UTF-8
        或读取过程中发生 I/O 错误，返回 0。
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件行数，读取失败时返回 0
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except (UnicodeDecodeError, IOError):
            return 0
    
    @staticmethod
    def ensure_output_path(input_file: Path, input_root: Path, output_root: Path) -> Path:
        """
        保持目录结构，生成输出路径。
        
        根据输入文件相对于输入根目录的路径，在输出根目录下创建
        相同的目录结构，并返回完整的输出文件路径。会自动创建
        所需的父目录。
        
        Args:
            input_file: 输入文件的完整路径
            input_root: 输入文件的根目录
            output_root: 输出文件的根目录
        
        Returns:
            输出文件的完整路径，父目录会被自动创建
        
        示例:
            >>> input_file = Path("/project/src/main.py")
            >>> input_root = Path("/project")
            >>> output_root = Path("/output")
            >>> output_path = FileScanner.ensure_output_path(
            ...     input_file, input_root, output_root
            ... )
            >>> print(output_path)  # /output/src/main.py
            >>> output_path.parent.exists()  # True（自动创建）
        
        注意:
            此方法为静态方法，可在不创建 FileScanner 实例时使用。
        """
        relative_path = input_file.relative_to(input_root)
        output_path = Path(output_root) / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path