# packages/comment/src/magicc_comment/utils/prompt_template_loader.py

from pathlib import Path
from typing import Optional
import logging


class PromptTemplateLoader:
    """Prompt模板加载器"""
    
    def __init__(self):
        self._cache: Optional[str] = None
        self._template_path: Optional[Path] = None
    
    def load_template(self, config_path: Optional[str] = None) -> str:
        """
        加载prompt模板
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认模板
            
        Returns:
            模板字符串
        """
        # 如果已缓存且路径相同，直接返回缓存
        if self._cache is not None:
            new_path = Path(config_path) if config_path else None
            if self._template_path == new_path:
                return self._cache
        
        # 加载模板
        if config_path:
            template = self._load_from_file(config_path)
            if template:
                self._cache = template
                self._template_path = Path(config_path)
                return template
        
        # 使用默认模板
        template = self._get_default_template()
        self._cache = template
        self._template_path = None
        return template
    
    def _load_from_file(self, file_path: str) -> Optional[str]:
        """从文件加载模板"""
        path = Path(file_path)
        
        if not path.exists():
            print(f"⚠️  Prompt配置文件不存在: {path}")
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 验证模板是否包含必需的占位符
            if '{method_signature}' not in template:
                print(f"⚠️  Prompt模板缺少 {{method_signature}} 占位符: {path}")
                return None
            
            print(f"📝 使用自定义Prompt模板: {path}")
            return template
            
        except Exception as e:
            print(f"⚠️  读取Prompt配置文件失败: {e}")
            return None
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """请为以下Java方法生成标准的JavaDoc注释。

            【重要约束】
            1. 必须严格忠于源码，不要修改任何内容
            2. throws声明的异常类型必须与原方法完全一致
            3. 参数名必须与原方法完全一致（不要修正拼写错误）
            4. 不要添加源码中没有的异常类型
            5. 返回类型必须与实际返回类型一致

            方法签名：
            {method_signature}

            请只输出JavaDoc注释部分，格式如下：
            /**
            * 功能描述
            *
            * @param 参数名1 参数说明
            * @param 参数名2 参数说明
            * @return 返回值说明
            * @throws 异常类型 异常说明
            */
            """
    
    def clear_cache(self):
        """清除缓存"""
        self._cache = None
        self._template_path = None
    
    def reload(self, config_path: Optional[str] = None) -> str:
        """强制重新加载模板"""
        self.clear_cache()
        return self.load_template(config_path)