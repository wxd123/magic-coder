# magic-coder/shared/src/magicc-shared/data_access/model/share_models.py - 当前版本表结构

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from magic_base import BaseModel

Base = declarative_base()


class Project(Base,BaseModel):
    """项目表 - 记录被检测的源代码项目"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)     # 项目名称（唯一）
    source_path = Column(String(500), nullable=False)           # 原始源代码路径
    work_dir = Column(String(500), nullable=False)              # 工作目录路径
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # 关系
    methods = relationship("Method", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_project_name', 'name'),
        Index('idx_created_at', 'created_at'),
    )

class SourceFile(Base, BaseModel):
    """
    源代码文件表
    
    记录项目中的每个 Java 源文件
    一条记录 = 一个项目 + 一个源文件
    """
    __tablename__ = "source_files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # 文件信息
    file_path = Column(String(500), nullable=False)             # 相对路径
    file_name = Column(String(255), nullable=False)             # 文件名
    file_size = Column(Integer)                                 # 文件大小(字节)
    
    # 文件内容哈希（用于增量更新）
    file_hash = Column(String(64), nullable=False)              # SHA256哈希
    
    # 统计信息
    total_methods = Column(Integer, default=0)                  # 文件中的方法总数
    total_lines = Column(Integer, default=0)                    # 文件总行数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # 关系
    project = relationship("Project", back_populates="source_files")
    methods = relationship("Method", back_populates="source_file", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'file_path', name='uq_source_file_project_path'),
        Index('idx_source_file_project', 'project_id'),
        Index('idx_source_file_hash', 'file_hash'),
        Index('idx_source_file_path', 'project_id', 'file_path'),
    )


class Method(Base, BaseModel):
    """
    方法表 - 存储从源代码解析出的方法信息
    
    一条记录 = 一个项目中 的一个方法
    """
    __tablename__ = "methods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # 源代码定位
    file_path = Column(String(500), nullable=False)             # 相对路径
    line_number = Column(Integer, nullable=False)               # 方法声明行号
    
    # 方法签名信息
    method_name = Column(String(255), nullable=False)
    signature = Column(String(500), nullable=False)             # 完整方法签名
    return_type = Column(String(100))                           # 返回类型
    parameters_json = Column(Text)                              # JSON格式: ["param1", "param2"]
    
    # 源代码内容
    source_code = Column(Text, nullable=False)                  # 方法完整源码
    hash_code = Column(String(64), nullable=False)              # SHA256哈希，用于增量检测
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # 关系
    project = relationship("Project", back_populates="methods")
    comments = relationship("Comment", back_populates="method", cascade="all, delete-orphan")
    qc_items = relationship("QCItem", back_populates="method", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_method_project', 'project_id'),
        Index('idx_method_name', 'project_id', 'method_name'),
        Index('idx_method_file', 'project_id', 'file_path'),
        Index('idx_method_hash', 'hash_code'),
        UniqueConstraint('project_id', 'file_path', 'signature', name='uq_method_project_signature'),
    )





class Task(Base, BaseModel):
    """
    任务表 - 追踪工作流状态
    
    用于记录 clean/generate/qc 等长时间任务的执行状态
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # 任务标识
    task_type = Column(String(50), nullable=False)               # clean / generate / qc
    task_uuid = Column(String(36), nullable=False, unique=True)  # 任务唯一标识
    
    # 任务参数（JSON）
    parameters_json = Column(Text)                               # 任务参数，如模型名称等
    
    # 状态
    status = Column(String(20), nullable=False, default='pending')  # pending / running / success / failed / cancelled
    
    # 进度统计
    total_items = Column(Integer, default=0)                     # 总处理项数
    processed_items = Column(Integer, default=0)                 # 已处理项数
    failed_items = Column(Integer, default=0)                    # 失败项数
    
    # 结果
    result_summary = Column(Text)                                # 结果摘要（JSON）
    error_message = Column(Text)                                 # 错误信息
    
    # 时间戳
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    
    __table_args__ = (
        Index('idx_task_project', 'project_id'),
        Index('idx_task_type', 'task_type'),
        Index('idx_task_status', 'status'),
        Index('idx_task_uuid', 'task_uuid'),
        Index('idx_task_created', 'created_at'),
    )