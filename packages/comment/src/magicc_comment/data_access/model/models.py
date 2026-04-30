# models.py - 当前版本表结构

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from magic_base import BaseModel

Base = declarative_base()



class Comment(Base, BaseModel):
    """
    注释表 - 存储生成的注释
    
    一条记录 = 一个方法 + 一个模型 + 一次生成
    """
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    method_id = Column(Integer, ForeignKey("methods.id", ondelete="CASCADE"), nullable=False)
    
    # 生成信息
    model_name = Column(String(100), nullable=False)             # gpt-4 / claude-3 / deepseek
    content = Column(Text)                                       # 生成的注释内容
    
    # LLM响应详情
    raw_response = Column(Text)                                  # LLM原始响应
    generation_time = Column(Float)                              # 生成耗时(秒)
    prompt_tokens = Column(Integer)                              # 输入token数
    completion_tokens = Column(Integer)                          # 输出token数
    
    # 状态
    success = Column(Integer, default=1)                         # 是否成功（1=成功，0=失败）
    error_message = Column(Text)                                 # 错误信息
    
    # 时间戳
    generated_at = Column(DateTime, default=datetime.now)
    
    # 关系
    method = relationship("Method", back_populates="comments")
    qc_items = relationship("QCItem", back_populates="comment", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_comment_method', 'method_id'),
        Index('idx_comment_model', 'method_id', 'model_name'),
        Index('idx_comment_success', 'success'),
        Index('idx_generated_at', 'generated_at'),
    )


class Metric(Base, BaseModel):
    """
    指标元数据表 - 定义所有质量指标
    
    新增指标时，只需在此表插入一条记录，无需改代码
    """
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)       # format / completeness / param_match
    name = Column(String(100), nullable=False)                   # 格式正确性 / 内容完整性
    description = Column(Text)                                   # 指标详细说明
    category = Column(String(50))                                # syntax / semantic / style
    
    # 默认配置
    default_weight = Column(Float, default=0.2)                  # 默认权重
    default_threshold = Column(Float, default=60.0)              # 默认通过阈值
    
    # 状态
    enabled = Column(Integer, default=1)                         # 是否启用
    sort_order = Column(Integer, default=0)                      # 排序顺序
    
    # 版本信息
    version = Column(String(20), default='1.0.0')
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_metric_code', 'code'),
        Index('idx_metric_enabled', 'enabled'),
    )


class QCItem(Base, BaseModel):
    """
    质检明细表 - 存储每个检测维度的结果
    
    一条记录 = 一个方法 + 一条注释 + 一个指标 + 一种检测方式
    """
    __tablename__ = "qc_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False)
    method_id = Column(Integer, ForeignKey("methods.id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    
    # 检测标识
    validator_type = Column(String(20), nullable=False)          # rule / llm
    
    # 检测结果
    score = Column(Float, nullable=False)                        # 得分 0-100
    passed = Column(Integer, default=0)                          # 是否通过（1=通过，0=未通过）
    details = Column(Text)                                       # 详细说明
    
    # 问题与建议（JSON格式存储）
    issues_json = Column(Text)                                   # ["问题1", "问题2"]
    suggestions_json = Column(Text)                              # ["建议1", "建议2"]
    
    # 元信息
    threshold = Column(Float, default=60.0)                      # 实际使用的阈值
    duration_ms = Column(Integer)                                # 检测耗时(毫秒)
    
    # 时间戳
    checked_at = Column(DateTime, default=datetime.now)
    
    # 关系
    comment = relationship("Comment", back_populates="qc_items")
    method = relationship("Method", back_populates="qc_items")
    metric = relationship("Metric")
    
    __table_args__ = (
        # 确保同一条注释的同一个指标同一种检测方式只有一条记录
        UniqueConstraint('comment_id', 'metric_id', 'validator_type', name='uq_qc_unique'),
        # 索引
        Index('idx_qc_comment', 'comment_id'),
        Index('idx_qc_method', 'method_id'),
        Index('idx_qc_metric', 'metric_id'),
        Index('idx_qc_score', 'score'),
        Index('idx_qc_passed', 'passed'),
        Index('idx_qc_validator', 'validator_type'),
        Index('idx_qc_checked_at', 'checked_at'),
    )


