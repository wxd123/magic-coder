# `magicc_comment`

## Table of Contents

- 🅼 [magicc\_comment](#magicc_comment)
- 🅼 [magicc\_comment\.cli](#magicc_comment-cli)
- 🅼 [magicc\_comment\.cli\.cli](#magicc_comment-cli-cli)
- 🅼 [magicc\_comment\.command](#magicc_comment-command)
- 🅼 [magicc\_comment\.command\.container](#magicc_comment-command-container)
- 🅼 [magicc\_comment\.command\.java](#magicc_comment-command-java)
- 🅼 [magicc\_comment\.command\.java\.clean\_command](#magicc_comment-command-java-clean_command)
- 🅼 [magicc\_comment\.command\.java\.compare\_report\_command](#magicc_comment-command-java-compare_report_command)
- 🅼 [magicc\_comment\.command\.java\.generate\_command](#magicc_comment-command-java-generate_command)
- 🅼 [magicc\_comment\.command\.java\.prompt\_command](#magicc_comment-command-java-prompt_command)
- 🅼 [magicc\_comment\.command\.java\.qc\_command](#magicc_comment-command-java-qc_command)
- 🅼 [magicc\_comment\.command\.java\.report\_command](#magicc_comment-command-java-report_command)
- 🅼 [magicc\_comment\.pipeline](#magicc_comment-pipeline)
- 🅼 [magicc\_comment\.pipeline\.command\_executor](#magicc_comment-pipeline-command_executor)
- 🅼 [magicc\_comment\.pipeline\.executor](#magicc_comment-pipeline-executor)

<a name="magicc_comment"></a>
## 🅼 magicc\_comment
<a name="magicc_comment-cli"></a>
## 🅼 magicc\_comment\.cli
<a name="magicc_comment-cli-cli"></a>
## 🅼 magicc\_comment\.cli\.cli

Magic Comment - 代码注释生成工具

- **Functions:**
  - 🅵 [find\_config\_files](#magicc_comment-cli-cli-find_config_files)
  - 🅵 [main](#magicc_comment-cli-cli-main)
  - 🅵 [cmd\_run](#magicc_comment-cli-cli-cmd_run)
  - 🅵 [cmd\_clean](#magicc_comment-cli-cli-cmd_clean)

### Functions

<a name="magicc_comment-cli-cli-find_config_files"></a>
### 🅵 magicc\_comment\.cli\.cli\.find\_config\_files

```python
def find_config_files(config_path):
```

在指定路径下自动查找配置文件

**Parameters:**

- **config_path**: 配置目录路径

**Returns:**

- `tuple`: \(pipeline\_config\_path, prompt\_config\_path\)
<a name="magicc_comment-cli-cli-main"></a>
### 🅵 magicc\_comment\.cli\.cli\.main

```python
def main():
```
<a name="magicc_comment-cli-cli-cmd_run"></a>
### 🅵 magicc\_comment\.cli\.cli\.cmd\_run

```python
def cmd_run(args):
```

执行 Pipeline
<a name="magicc_comment-cli-cli-cmd_clean"></a>
### 🅵 magicc\_comment\.cli\.cli\.cmd\_clean

```python
def cmd_clean(args):
```

仅执行清理
<a name="magicc_comment-command"></a>
## 🅼 magicc\_comment\.command
<a name="magicc_comment-command-container"></a>
## 🅼 magicc\_comment\.command\.container

- **Functions:**
  - 🅵 [regist\_command](#magicc_comment-command-container-regist_command)

### Functions

<a name="magicc_comment-command-container-regist_command"></a>
### 🅵 magicc\_comment\.command\.container\.regist\_command

```python
def regist_command(types: str):
```

通用命令注册入口

**Parameters:**

- **types**: 语言类型 \(java, python, go, rust\)
<a name="magicc_comment-command-java"></a>
## 🅼 magicc\_comment\.command\.java
<a name="magicc_comment-command-java-clean_command"></a>
## 🅼 magicc\_comment\.command\.java\.clean\_command

- **Classes:**
  - 🅲 [CleanCommand](#magicc_comment-command-java-clean_command-CleanCommand)

### Classes

<a name="magicc_comment-command-java-clean_command-CleanCommand"></a>
### 🅲 magicc\_comment\.command\.java\.clean\_command\.CleanCommand

```python
class CleanCommand(Command):
```

清理Java源码注释的命令

**Functions:**

<a name="magicc_comment-command-java-clean_command-CleanCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.clean\_command\.CleanCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-command-java-compare_report_command"></a>
## 🅼 magicc\_comment\.command\.java\.compare\_report\_command

- **Classes:**
  - 🅲 [CompareReportCommand](#magicc_comment-command-java-compare_report_command-CompareReportCommand)

### Classes

<a name="magicc_comment-command-java-compare_report_command-CompareReportCommand"></a>
### 🅲 magicc\_comment\.command\.java\.compare\_report\_command\.CompareReportCommand

```python
class CompareReportCommand(Command):
```

生成模型对比报告

**Functions:**

<a name="magicc_comment-command-java-compare_report_command-CompareReportCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.compare\_report\_command\.CompareReportCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-command-java-generate_command"></a>
## 🅼 magicc\_comment\.command\.java\.generate\_command

- **Classes:**
  - 🅲 [GenerateCommand](#magicc_comment-command-java-generate_command-GenerateCommand)

### Classes

<a name="magicc_comment-command-java-generate_command-GenerateCommand"></a>
### 🅲 magicc\_comment\.command\.java\.generate\_command\.GenerateCommand

```python
class GenerateCommand(LLMCommand):
```

生成注释命令

功能：为Java代码中的方法生成标准的JavaDoc注释

**Functions:**

<a name="magicc_comment-command-java-generate_command-GenerateCommand-__init__"></a>
#### 🅵 magicc\_comment\.command\.java\.generate\_command\.GenerateCommand\.\_\_init\_\_

```python
def __init__(self):
```
<a name="magicc_comment-command-java-generate_command-GenerateCommand-set_task_info"></a>
#### 🅵 magicc\_comment\.command\.java\.generate\_command\.GenerateCommand\.set\_task\_info

```python
def set_task_info(self, task_info: Dict[str, Any]):
```

设置任务信息（由 executor 调用）
<a name="magicc_comment-command-java-generate_command-GenerateCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.generate\_command\.GenerateCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-command-java-prompt_command"></a>
## 🅼 magicc\_comment\.command\.java\.prompt\_command

- **Classes:**
  - 🅲 [PromptCommand](#magicc_comment-command-java-prompt_command-PromptCommand)

### Classes

<a name="magicc_comment-command-java-prompt_command-PromptCommand"></a>
### 🅲 magicc\_comment\.command\.java\.prompt\_command\.PromptCommand

```python
class PromptCommand(Command):
```

为每个 Java 文件生成 prompt

**Functions:**

<a name="magicc_comment-command-java-prompt_command-PromptCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.prompt\_command\.PromptCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-command-java-qc_command"></a>
## 🅼 magicc\_comment\.command\.java\.qc\_command

- **Classes:**
  - 🅲 [QCCommand](#magicc_comment-command-java-qc_command-QCCommand)

### Classes

<a name="magicc_comment-command-java-qc_command-QCCommand"></a>
### 🅲 magicc\_comment\.command\.java\.qc\_command\.QCCommand

```python
class QCCommand(Command):
```

质量检查命令

**Functions:**

<a name="magicc_comment-command-java-qc_command-QCCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.qc\_command\.QCCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-command-java-report_command"></a>
## 🅼 magicc\_comment\.command\.java\.report\_command

- **Classes:**
  - 🅲 [ReportCommand](#magicc_comment-command-java-report_command-ReportCommand)

### Classes

<a name="magicc_comment-command-java-report_command-ReportCommand"></a>
### 🅲 magicc\_comment\.command\.java\.report\_command\.ReportCommand

```python
class ReportCommand(Command):
```

生成报告命令

**Functions:**

<a name="magicc_comment-command-java-report_command-ReportCommand-execute"></a>
#### 🅵 magicc\_comment\.command\.java\.report\_command\.ReportCommand\.execute

```python
def execute(self, ctx: Context) -> Result:
```
<a name="magicc_comment-pipeline"></a>
## 🅼 magicc\_comment\.pipeline
<a name="magicc_comment-pipeline-command_executor"></a>
## 🅼 magicc\_comment\.pipeline\.command\_executor

- **Classes:**
  - 🅲 [CommandExecutor](#magicc_comment-pipeline-command_executor-CommandExecutor)

### Classes

<a name="magicc_comment-pipeline-command_executor-CommandExecutor"></a>
### 🅲 magicc\_comment\.pipeline\.command\_executor\.CommandExecutor

```python
class CommandExecutor:
```

负责执行 pipeline 中的命令

**Functions:**

<a name="magicc_comment-pipeline-command_executor-CommandExecutor-__init__"></a>
#### 🅵 magicc\_comment\.pipeline\.command\_executor\.CommandExecutor\.\_\_init\_\_

```python
def __init__(self, models_config: Dict[str, Any], default_language: str = 'java'):
```
<a name="magicc_comment-pipeline-command_executor-CommandExecutor-execute_step"></a>
#### 🅵 magicc\_comment\.pipeline\.command\_executor\.CommandExecutor\.execute\_step

```python
def execute_step(self, ctx: Context, step: Dict[str, Any]) -> Result:
```

执行单个步骤
<a name="magicc_comment-pipeline-command_executor-CommandExecutor-release_resources"></a>
#### 🅵 magicc\_comment\.pipeline\.command\_executor\.CommandExecutor\.release\_resources

```python
def release_resources(self) -> Result:
```

释放所有模型资源
<a name="magicc_comment-pipeline-executor"></a>
## 🅼 magicc\_comment\.pipeline\.executor

- **Classes:**
  - 🅲 [PipelineExecutor](#magicc_comment-pipeline-executor-PipelineExecutor)

### Classes

<a name="magicc_comment-pipeline-executor-PipelineExecutor"></a>
### 🅲 magicc\_comment\.pipeline\.executor\.PipelineExecutor

```python
class PipelineExecutor:
```

Pipeline 执行器，负责协调整个流程

**Functions:**

<a name="magicc_comment-pipeline-executor-PipelineExecutor-__init__"></a>
#### 🅵 magicc\_comment\.pipeline\.executor\.PipelineExecutor\.\_\_init\_\_

```python
def __init__(self, config: Dict[str, Any]):
```
<a name="magicc_comment-pipeline-executor-PipelineExecutor-run"></a>
#### 🅵 magicc\_comment\.pipeline\.executor\.PipelineExecutor\.run

```python
def run(self, ctx: Context, pipeline_name: str = 'pipeline') -> Result:
```

运行 pipeline
