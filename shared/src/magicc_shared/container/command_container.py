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
    """命令容器 - 单例模式，全局唯一"""
    
    _instance: Optional['CommandContainer'] = None
    _commands: Dict[str, Dict[str, Type[Command]]] = {}
    
    def __new__(cls) -> 'CommandContainer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
        return cls._instance
    
    def register(self, language: str, name: str, cmd_class: Type[Command]) -> None:
        """
        注册命令
        
        Args:
            language: 语言标识 (java, python, go, rust)
            name: 命令名 (clean, prompt, generate, qc, report)
            cmd_class: 命令类 (必须继承 Command)
        
        Raises:
            TypeError: 如果 cmd_class 不是 Command 的子类
            ValueError: 如果 language 或 name 为空
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
        获取命令类
        
        Args:
            language: 语言标识
            name: 命令名
        
        Returns:
            命令类，如果不存在返回 None
        """
        lang_commands = self._commands.get(language)
        if lang_commands:
            return lang_commands.get(name)
        return None
    
    def get_with_default(self, language: str, name: str, default_language: str = "java") -> Optional[Type[Command]]:
        """
        获取命令类，支持回退到默认语言
        
        Args:
            language: 首选语言
            name: 命令名
            default_language: 默认语言（找不到时使用）
        
        Returns:
            命令类，如果都不存在返回 None
        """
        cmd = self.get(language, name)
        if cmd is None and language != default_language:
            cmd = self.get(default_language, name)
        return cmd
    
    def has(self, language: str, name: str) -> bool:
        """检查命令是否存在"""
        return self.get(language, name) is not None
    
    def get_by_language(self, language: str) -> Dict[str, Type[Command]]:
        """获取指定语言的所有命令"""
        return self._commands.get(language, {}).copy()
    
    def get_by_name(self, name: str) -> Dict[str, Type[Command]]:
        """获取所有语言中指定名称的命令"""
        result = {}
        for language, commands in self._commands.items():
            if name in commands:
                result[language] = commands[name]
        return result
    
    def get_commands_requiring_llm(self, language: str = None) -> List[Tuple[str, str, Type[Command]]]:
        """
        获取需要 LLM 的命令列表
        
        Args:
            language: 可选，指定语言
        
        Returns:
            (language, name, cmd_class) 列表
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
        列出所有已注册的命令
        
        Returns:
            {language: {name: class_path}}
        """
        result = {}
        for language, commands in self._commands.items():
            result[language] = {
                name: f"{cmd_class.__module__}.{cmd_class.__name__}"
                for name, cmd_class in commands.items()
            }
        return result
    
    def list_languages(self) -> List[str]:
        """列出所有已注册的语言"""
        return list(self._commands.keys())
    
    def remove(self, language: str, name: str) -> bool:
        """
        移除命令
        
        Returns:
            是否成功移除
        """
        if language in self._commands and name in self._commands[language]:
            del self._commands[language][name]
            return True
        return False
    
    def remove_language(self, language: str) -> bool:
        """移除整个语言的所有命令"""
        if language in self._commands:
            del self._commands[language]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有命令"""
        self._commands.clear()
    
    def size(self) -> int:
        """获取注册的命令总数"""
        return sum(len(cmds) for cmds in self._commands.values())
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return self.size() == 0


# 全局单例实例
_command_container = CommandContainer()


# ============ 便捷函数 ============

def register_command(language: str, name: str, cmd_class: Type[Command]) -> None:
    """注册命令"""
    _command_container.register(language, name, cmd_class)


def get_command(language: str, name: str) -> Optional[Type[Command]]:
    """获取命令"""
    return _command_container.get(language, name)


def get_command_with_default(language: str, name: str, default_language: str = "java") -> Optional[Type[Command]]:
    """获取命令（支持默认语言回退）"""
    return _command_container.get_with_default(language, name, default_language)


def has_command(language: str, name: str) -> bool:
    """检查命令是否存在"""
    return _command_container.has(language, name)


def get_commands_by_language(language: str) -> Dict[str, Type[Command]]:
    """获取指定语言的所有命令"""
    return _command_container.get_by_language(language)


def get_commands_by_name(name: str) -> Dict[str, Type[Command]]:
    """获取所有语言中指定名称的命令"""
    return _command_container.get_by_name(name)


def list_all_commands() -> Dict[str, Dict[str, str]]:
    """列出所有命令"""
    return _command_container.list_all()


def list_languages() -> List[str]:
    """列出所有语言"""
    return _command_container.list_languages()


def remove_command(language: str, name: str) -> bool:
    """移除命令"""
    return _command_container.remove(language, name)


def clear_all_commands() -> None:
    """清空所有命令"""
    _command_container.clear()


def get_command_container() -> CommandContainer:
    """获取命令容器实例"""
    return _command_container


# ============ 装饰器语法糖 ============

def command(language: str, name: str):
    """
    装饰器：自动注册命令
    
    使用方式:
        @command("java", "clean")
        class JavaCleanCommand(Command):
            ...
    """
    def decorator(cls):
        register_command(language, name, cls)
        return cls
    return decorator