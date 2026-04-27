# Magic-coder

[![PyPI version](https://badge.fury.io/py/magicc.svg)](https://badge.fury.io/py/magicc)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> AI辅助代码生成全家桶 —— 提供注释、代码、架构、测试及质量报告等全链路支持

## 项目状态

**开发中** - 首个正式版本将于 2026 年 8 月发布

## 功能规划

|      子包           | 说明    | 状态    |
|--------------------|--------|--------|
| `magicc-comment`   | 注释生成 | 开发中  |
| `magicc-code`      | 代码生成 | 规划中  |
| `magicc-arch`      | 架构生成 | 规划中  |
| `magicc-test`      | 测试生成 | 规划中  |
| `magicc-report`    | 质量报告 | 规划中  |

## 快速开始

# 安装所有子包
```bash
pip install magicc-comment magicc-code magicc-arch magicc-test magicc-report
```
# 或只安装需要的
```bash
pip install magicc-comment
```

## 开发
```bash
git clone https://github.com/wxd123/magicc.git
cd magicc
```


## 代码规范
本项目遵循以下基本原则：

1. 单文件不超过 200 行：超过时请拆分为多个模块
2. 单函数不超过 200 行：超过时请拆分为多个小函数
3. 注释尽量完整：关键逻辑、复杂算法、非显而易见的代码必须有注释说明
4. 如有特殊场景确实需要突破（如纯数据定义文件），可在 PR 中说明。

这些规则旨在保证代码的可读性和可维护性，便于合作，请尽量遵守。

## 针对 AI 辅助工具的提示
本项目使用 AI 辅助开发，请在生成代码时尽量遵守上述代码规范。

## 许可证
MIT License

## 作者
[wxd123](https://github.com/wxd123)

It's production-grade, don't be magic. 
