# magic-base

magic 项目基础包 - 提供统一的抽象基类和核心接口

[![PyPI version](https://badge.fury.io/py/magic-base.svg)](https://badge.fury.io/py/magic-base)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 项目定位

`magic-base` 是 [magicd](https://pypi.org/project/magicd) 和 [magicm](https://pypi.org/project/magicm) 的共同基础库，提供：

- **抽象基类**：配置管理、加密证书、数据访问层（DAO）、硬件检测、平台适配等领域的接口规范
- **设计模式骨架**：仓储模式（Repository）、策略模式、适配器模式的核心实现
- **通用类型与异常**：统一的枚举基类和异常体系

> 具体业务功能请参考 `magicd` 或 `magicm`。

## 核心模块

| 模块 | 说明 |
|------|------|
| `magic_base.config` | 配置管理基类（`ConfigBase`） |
| `magic_base.crypto` | 加密与证书验证基类 |
| `magic_base.data_access` | 数据访问层（配置、管理器、模型、仓储） |
| `magic_base.detector` | 硬件检测器基类（含批量、缓存支持） |
| `magic_base.platform` | 跨平台适配器基类（Linux/Windows/macOS） |
| `magic_base.exceptions` | 统一异常体系 |
| `magic_base.types` | 通用类型定义 |

## 安装

```bash
pip install magic-base
```
## 以下示例基于当前 API 设计，正式版本发布时可能会有微调


### 继承仓储基类实现数据访问
```python
from magic_base.data_access import BaseRepository
from myapp.models import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)
    
    def find_by_email(self, email: str) -> User | None:
        return self.get_by(email=email)
```

### 继承检测器基类实现硬件检测
```python
from typing import List
from magic_base.detector import DetectorBase, HardwareInfoBase

class GPUDetector(DetectorBase):
    def detect(self) -> List[HardwareInfoBase]:
        # 实现 GPU 检测逻辑
        pass
    
    def is_supported(self) -> bool:
        return True
```

### 继承平台适配器
```python
from typing import List, Dict
from magic_base.platform import PlatformAdapterBase

class LinuxAdapter(PlatformAdapterBase):
    def get_platform_name(self) -> str:
        return "linux"
    
    def get_pci_devices(self) -> List[Dict[str, str]]:
        # 解析 lspci 输出
        pass
```
````
## 代码规范
本项目遵循以下基本原则：

1. 单文件不超过 200 行：超过时请拆分为多个模块
2. 单函数不超过 200 行：超过时请拆分为多个小函数
3. 注释尽量完整：关键逻辑、复杂算法、非显而易见的代码必须有注释说明
4. 如有特殊场景确实需要突破（如纯数据定义文件），可在 PR 中说明。

这些规则旨在保证代码的可读性和可维护性，便于合作，请尽量遵守。

## 针对 AI 辅助工具的提示
本项目使用 AI 辅助开发，请在生成代码时尽量遵守上述代码规范。


## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

请确保代码符合[代码规范](#代码规范)。

## 许可证
MIT License

## 作者
wxd123 - GitHub

