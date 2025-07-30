from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float
from sqlalchemy.sql import func
from .base import Base

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    level = Column(String(10), nullable=False, index=True)  # debug, info, warning, error
    module = Column(String(50), nullable=False, index=True)  # system, user, api, database
    message = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    user_name = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)  # 额外的日志详情
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemBackup(Base):
    """系统备份表"""
    __tablename__ = "system_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    backup_type = Column(String(20), nullable=False)  # full, incremental
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")  # in_progress, completed, failed
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 备份内容统计
    tables_count = Column(Integer, nullable=True)
    records_count = Column(Integer, nullable=True)
    files_count = Column(Integer, nullable=True)

class SystemMetric(Base):
    """系统指标表"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metric_type = Column(String(50), nullable=False, index=True)  # cpu, memory, disk, network
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)  # %, MB, GB, etc.
    details = Column(JSON, nullable=True)  # 额外的指标详情
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PerformanceMetric(Base):
    """性能指标表"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    response_time = Column(Float, nullable=False)  # 响应时间（毫秒）
    status_code = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_size = Column(Integer, nullable=True)  # 请求大小（字节）
    response_size = Column(Integer, nullable=True)  # 响应大小（字节）
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelUsageMetric(Base):
    """模型使用指标表"""
    __tablename__ = "model_usage_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    model_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    total_calls = Column(Integer, nullable=False, default=0)
    success_calls = Column(Integer, nullable=False, default=0)
    failed_calls = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    total_cost = Column(Float, nullable=False, default=0.0)
    avg_response_time = Column(Float, nullable=False, default=0.0)
    min_response_time = Column(Float, nullable=True)
    max_response_time = Column(Float, nullable=True)
    error_details = Column(JSON, nullable=True)  # 错误详情
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), nullable=False, unique=True, index=True)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(20), nullable=False, default="string")  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, nullable=False, default=False)  # 是否敏感配置
    updated_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ServiceHealth(Base):
    """服务健康状态表"""
    __tablename__ = "service_health"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # healthy, warning, error
    response_time = Column(Float, nullable=True)  # 响应时间（毫秒）
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    error_message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)  # 服务详情
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemAlert(Base):
    """系统告警表"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # cpu, memory, disk, error_rate
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    metric_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    is_resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 