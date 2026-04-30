# magicc_shared/container/command_container.py
"""
命令容器模块 - 统一管理所有命令的注册和获取

两层设计:
- 第一层: 语言 (java, python, go, rust)
- 第二层: 命令名 (clean, prompt, generate, qc, report)
"""

from typing import Dict, Type, Optional, List, Tuple
from magicc_shared.core import Command, LLMCommand


class CommandContainer:
    """
    命令容器 - 单例模式，全局唯一
    
    提供命令的注册、查询、删除等管理功能。采用两层结构组织命令：
    第一层按编程语言分类，第二层按命令名称分类。
    
    设计模式:
        - 单例模式: 全局只有一个容器实例
        - 注册表模式: 集中管理所有命令类
    
    示例:
        >>> container = CommandContainer()
        >>> container.register("java", "clean", JavaCleanCommand)
        >>> cmd_class = container.get("java", "clean")
        
        >>> # 使用便捷函数
        >>> from magicc_shared.container import register_command
        >>> register_command("python", "generate", PythonGenerateCommand)
    """
    
    _instance: Optional['CommandContainer'] = None
    """单例实例"""
    
    _commands: Dict[str, Dict[str, Type[Command]]] = {}
    """存储命令的嵌套字典: {language: {command_name: command_class}}"""
    
    def __new__(cls) -> 'CommandContainer':
        """
        实现单例模式，确保全局只有一个容器实例。
        
        Returns:
            CommandContainer 的单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
        return cls._instance
    
    def register(self, language: str, name: str, cmd_class: Type[Command]) -> None:
        """
        注册命令到容器中。
        
        Args:
            language: 语言标识，如 "java", "python", "go", "rust"
            name: 命令名，如 "clean", "prompt", "generate", "qc", "report"
            cmd_class: 命令类，必须继承自 Command
        
        Raises:
            TypeError: 如果 cmd_class 不是 Command 的子类
            ValueError: 如果 language 或 name 为空字符串
        
        示例:
            >>> container.register("python", "analyze", PythonAnalyzeCommand)
        """
        if not issubclass(cmd_class, Command):
            raise TypeError(f"{cmd_class.__name__} must be a subclass of Command")
        
        if not language or not name:
            raise ValueError(f"Language and name cannot be empty: {language}:{name}")
        
        if language not in self._commands:
            self._commands[language] = {}
        
        self._commands[language][name] = cmd_class
    
    def get(self, language: str, name: str) -> Optional[Type[Command]]:
        """
        获取命令类。
        
        Args:
            language: 语言标识
            name: 命令名
        
        Returns:
            命令类，如果不存在返回 None
        
        示例:
            >>> cmd_class = container.get("java", "clean")
            >>> if cmd_class:
            ...     result = cmd_class().execute(ctx)
        """
        lang_commands = self._commands.get(language)
        if lang_commands:
            return lang_commands.get(name)
        return None
    
    def get_with_default(self, language: str, name: str, default_language: str = "java") -> Optional[Type[Command]]:
        """
        获取命令类，支持回退到默认语言。
        
        当指定语言中找不到命令时，自动尝试从默认语言中获取。
        
        Args:
            language: 首选语言
            name: 命令名
            default_language: 默认语言（首选语言找不到时使用），默认为 "java"
        
        Returns:
            命令类，如果都不存在返回 None
        
        示例:
            >>> # 如果 python 中没有 clean 命令，会尝试获取 java 的 clean 命令
            >>> cmd = container.get_with_default("python", "clean", default_language="java")
        """
        cmd = self.get(language, name)
        if cmd is None and language != default_language:
            cmd = self.get(default_language, name)
        return cmd
    
    def has(self, language: str, name: str) -> bool:
        """
        检查命令是否存在。
        
        Args:
            language: 语言标识
            name: 命令名
        
        Returns:
            命令存在返回 True，否则返回 False
        """
        return self.get(language, name) is not None
    
    def get_by_language(self, language: str) -> Dict[str, Type[Command]]:
        """
        获取指定语言的所有命令。
        
        Args:
            language: 语言标识
        
        Returns:
            字典的副本，键为命令名，值为命令类；如果语言不存在则返回空字典
        
        示例:
            >>> java_commands = container.get_by_language("java")
            >>> for name, cmd_class in java_commands.items():
            ...     print(f"{name}: {cmd_class.__name__}")
        """
        return self._commands.get(language, {}).copy()
    
    def get_by_name(self, name: str) -> Dict[str, Type[Command]]:
        """
        获取所有语言中指定名称的命令。
        
        跨语言搜索相同命令名的实现。
        
        Args:
            name: 命令名
        
        Returns:
            字典，键为语言名，值为命令类；如果找不到则返回空字典
        
        示例:
            >>> clean_commands = container.get_by_name("clean")
            >>> # 可能返回 {"java": JavaCleanCommand, "python": PythonCleanCommand}
        """
        result = {}
        for language, commands in self._commands.items():
            if name in commands:
                result[language] = commands[name]
        return result
    
    def get_commands_requiring_llm(self, language: str = None) -> List[Tuple[str, str, Type[Command]]]:
        """
        获取需要 LLM 的命令列表。
        
        筛选出所有继承自 LLMCommand 的命令。
        
        Args:
            language: 可选，指定语言；若为 None 则搜索所有语言
        
        Returns:
            (language, name, cmd_class) 元组的列表
        
        示例:
            >>> # 获取所有需要 LLM 的命令
            >>> llm_cmds = container.get_commands_requiring_llm()
            >>> for lang, name, cmd_class in llm_cmds:
            ...     print(f"{lang}.{name}: {cmd_class.__name__}")
            
            >>> # 只获取 Python 中需要 LLM 的命令
            >>> python_llm = container.get_commands_requiring_llm("python")
        """
        result = []
        languages = [language] if language else self._commands.keys()
        
        for lang in languages:
            for name, cmd_class in self._commands.get(lang, {}).items():
                if issubclass(cmd_class, LLMCommand):
                    result.append((lang, name, cmd_class))
        return result
    
    def list_all(self) -> Dict[str, Dict[str, str]]:
        """
        列出所有已注册的命令。
        
        Returns:
            嵌套字典，格式为 {language: {name: class_path}}，
            其中 class_path 为 "模块名.类名" 格式的字符串
        
        示例:
            >>> all_cmds = container.list_all()
            >>> # 返回示例:
            >>> # {
            >>> #     "java": {"clean": "java_commands.clean.JavaCleanCommand"},
            >>> #     "python": {"generate": "python_commands.generate.PythonGenerateCommand"}
            >>> # }
        """
        result = {}
        for language, commands in self._commands.items():
            result[language] = {
                name: f"{cmd_class.__module__}.{cmd_class.__name__}"
                for name, cmd_class in commands.items()
            }
        return result
    
    def list_languages(self) -> List[str]:
        """
        列出所有已注册的语言。
        
        Returns:
            语言标识符列表
        
        示例:
            >>> languages = container.list_languages()
            >>> print(languages)  # ['java', 'python', 'go']
        """
        return list(self._commands.keys())
    
    def remove(self, language: str, name: str) -> bool:
        """
        移除指定的命令。
        
        Args:
            language: 语言标识
            name: 命令名
        
        Returns:
            成功移除返回 True，命令不存在返回 False
        """
        if language in self._commands and name in self._commands[language]:
            del self._commands[language][name]
            return True
        return False
    
    def remove_language(self, language: str) -> bool:
        """
        移除整个语言的所有命令。
        
        Args:
            language: 语言标识
        
        Returns:
            成功移除返回 True，语言不存在返回 False
        """
        if language in self._commands:
            del self._commands[language]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有已注册的命令。"""
        self._commands.clear()
    
    def size(self) -> int:
        """
        获取注册的命令总数。
        
        Returns:
            所有语言中命令的总数量
        """
        return sum(len(cmds) for cmds in self._commands.values())
    
    def is_empty(self) -> bool:
        """
        检查容器是否为空。
        
        Returns:
            没有任何命令时返回 True，否则返回 False
        """
        return self.size() == 0


# 全局单例实例
_command_container = CommandContainer()
"""
全局命令容器单例实例，供便捷函数使用。
通常不直接访问此变量，而是使用下面的便捷函数。
"""


# ============ 便捷函数 ============

def register_command(language: str, name: str, cmd_class: Type[Command]) -> None:
    """
    注册命令到全局容器。
    
    这是 register 方法的便捷函数版本。
    
    Args:
        language: 语言标识 (java, python, go, rust)
        name: 命令名 (clean, prompt, generate, qc, report)
        cmd_class: 命令类 (必须继承 Command)
    
    示例:
        >>> register_command("java", "clean", JavaCleanCommand)
    """
    _command_container.register(language, name, cmd_class)


def get_command(language: str, name: str) -> Optional[Type[Command]]:
    """
    从全局容器获取命令类。
    
    这是 get 方法的便捷函数版本。
    
    Args:
        language: 语言标识
        name: 命令名
    
    Returns:
        命令类，不存在时返回 None
    
    示例:
        >>> cmd_class = get_command("python", "generate")
    """
    return _command_container.get(language, name)


def get_command_with_default(language: str, name: str, default_language: str = "java") -> Optional[Type[Command]]:
    """
    获取命令类（支持默认语言回退）。
    
    这是 get_with_default 方法的便捷函数版本。
    
    Args:
        language: 首选语言
        name: 命令名
        default_language: 默认语言，默认为 "java"
    
    Returns:
        命令类，都不存在时返回 None
    """
    return _command_container.get_with_default(language, name, default_language)


def has_command(language: str, name: str) -> bool:
    """
    检查命令是否存在。
    
    这是 has 方法的便捷函数版本。
    
    Args:
        language: 语言标识
        name: 命令名
    
    Returns:
        存在返回 True，否则返回 False
    """
    return _command_container.has(language, name)


def get_commands_by_language(language: str) -> Dict[str, Type[Command]]:
    """
    获取指定语言的所有命令。
    
    这是 get_by_language 方法的便捷函数版本。
    
    Args:
        language: 语言标识
    
    Returns:
        命令字典 {命令名: 命令类}
    """
    return _command_container.get_by_language(language)


def get_commands_by_name(name: str) -> Dict[str, Type[Command]]:
    """
    获取所有语言中指定名称的命令。
    
    这是 get_by_name 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        字典 {语言名: 命令类}
    """
    return _command_container.get_by_name(name)


def list_all_commands() -> Dict[str, Dict[str, str]]:
    """
    列出所有命令。
    
    这是 list_all 方法的便捷函数版本。
    
    Returns:
        命令列表 {language: {name: class_path}}
    """
    return _command_container.list_all()


def list_languages() -> List[str]:
    """
    列出所有语言。
    
    这是 list_languages 方法的便捷函数版本。
    
    Returns:
        语言列表
    """
    return _command_container.list_languages()


def remove_command(language: str, name: str) -> bool:
    """
    移除命令。
    
    这是 remove 方法的便捷函数版本。
    
    Args:
        language: 语言标识
        name: 命令名
    
    Returns:
        成功移除返回 True
    """
    return _command_container.remove(language, name)


def clear_all_commands() -> None:
    """清空所有命令。"""
    _command_container.clear()


def get_command_container() -> CommandContainer:
    """
    获取命令容器实例。
    
    用于需要直接操作容器对象的场景。
    
    Returns:
        全局命令容器单例实例
    """
    return _command_container


# ============ 装饰器语法糖 ============

def command(language: str, name: str):
    """
    装饰器：自动注册命令到全局容器。
    
    使用此装饰器可以简化命令注册流程，无需显式调用 register_command。
    
    Args:
        language: 语言标识 (java, python, go, rust)
        name: 命令名 (clean, prompt, generate, qc, report)
    
    Returns:
        装饰器函数
    
    使用方式:
        @command("java", "clean")
        class JavaCleanCommand(Command):
            def execute(self, ctx: Context) -> Result:
                # 命令实现
                pass
    
    注意:
        被装饰的类必须继承自 Command 或其子类。
    """
    def decorator(cls):
        register_command(language, name, cls)
        return cls
    return decorator