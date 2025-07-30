from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 系统监控相关
class SystemMetrics(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU使用率")
    memory_usage: float = Field(..., ge=0, le=100, description="内存使用率")
    disk_usage: float = Field(..., ge=0, le=100, description="磁盘使用率")
    network_io: Dict[str, int] = Field(..., description="网络IO统计")
    uptime: float = Field(..., ge=0, description="系统运行时间（秒）")
    active_connections: int = Field(..., ge=0, description="活跃连接数")

class ServiceStatus(BaseModel):
    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    response_time: float = Field(..., ge=0, description="响应时间（秒）")
    last_check: str = Field(..., description="最后检查时间")
    details: Optional[str] = Field(None, description="详细信息")

class SystemStats(BaseModel):
    total_users: int = Field(..., ge=0, description="总用户数")
    total_knowledge_bases: int = Field(..., ge=0, description="总知识库数")
    total_documents: int = Field(..., ge=0, description="总文档数")
    total_chunks: int = Field(..., ge=0, description="总文档块数")
    total_queries: int = Field(..., ge=0, description="总查询数")
    active_sessions: int = Field(..., ge=0, description="活跃会话数")
    system_uptime: float = Field(..., ge=0, description="系统运行时间")

class PerformanceMetrics(BaseModel):
    api_response_time: Dict[str, float] = Field(..., description="API响应时间统计")
    error_rate: float = Field(..., ge=0, le=1, description="错误率")
    request_count: int = Field(..., ge=0, description="请求总数")
    success_rate: float = Field(..., ge=0, le=1, description="成功率")

class ModelMetrics(BaseModel):
    model_name: str = Field(..., description="模型名称")
    total_calls: int = Field(..., ge=0, description="总调用次数")
    success_calls: int = Field(..., ge=0, description="成功调用次数")
    failed_calls: int = Field(..., ge=0, description="失败调用次数")
    avg_response_time: float = Field(..., ge=0, description="平均响应时间")
    total_tokens: int = Field(..., ge=0, description="总token数")
    cost: float = Field(..., ge=0, description="总成本")
    last_used: str = Field(..., description="最后使用时间")

# 日志管理相关
class LogEntry(BaseModel):
    id: int = Field(..., description="日志ID")
    timestamp: str = Field(..., description="时间戳")
    level: str = Field(..., description="日志级别")
    module: str = Field(..., description="模块名称")
    message: str = Field(..., description="日志消息")
    user: Optional[str] = Field(None, description="用户")
    ip: Optional[str] = Field(None, description="IP地址")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")

class LogFilters(BaseModel):
    level: Optional[str] = Field(None, description="日志级别")
    module: Optional[str] = Field(None, description="模块")
    date_range: Optional[List[str]] = Field(None, description="日期范围")
    user: Optional[str] = Field(None, description="用户")
    search: Optional[str] = Field(None, description="搜索关键词")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(50, ge=1, le=500, description="每页大小")

class LogListResponse(BaseModel):
    logs: List[LogEntry] = Field(..., description="日志列表")
    total: int = Field(..., ge=0, description="总数")
    page: int = Field(..., ge=1, description="当前页")
    page_size: int = Field(..., ge=1, description="每页大小")

# 备份管理相关
class BackupInfo(BaseModel):
    id: int = Field(..., description="备份ID")
    filename: str = Field(..., description="文件名")
    size: int = Field(..., ge=0, description="文件大小")
    type: str = Field(..., description="备份类型")
    status: str = Field(..., description="备份状态")
    created_at: str = Field(..., description="创建时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")

class BackupCreate(BaseModel):
    type: str = Field(..., description="备份类型")
    description: Optional[str] = Field(None, description="备份描述")

# 系统配置相关
class SystemConfig(BaseModel):
    app_name: str = Field(..., description="应用名称")
    version: str = Field(..., description="版本号")
    debug: bool = Field(..., description="调试模式")
    log_level: str = Field(..., description="日志级别")
    max_file_size: int = Field(..., ge=0, description="最大文件大小")
    allowed_file_types: List[str] = Field(..., description="允许的文件类型")
    backup_retention_days: int = Field(..., ge=1, description="备份保留天数")

class SystemConfigUpdate(BaseModel):
    debug: Optional[bool] = Field(None, description="调试模式")
    log_level: Optional[str] = Field(None, description="日志级别")
    max_file_size: Optional[int] = Field(None, ge=0, description="最大文件大小")
    allowed_file_types: Optional[List[str]] = Field(None, description="允许的文件类型")
    backup_retention_days: Optional[int] = Field(None, ge=1, description="备份保留天数")

# 健康检查相关
class HealthCheck(BaseModel):
    name: str = Field(..., description="检查项名称")
    status: str = Field(..., description="状态")
    response_time: float = Field(..., ge=0, description="响应时间")
    details: Optional[str] = Field(None, description="详细信息")

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="整体状态")
    checks: List[HealthCheck] = Field(..., description="检查项列表")

# 实时监控相关
class RealtimeMetrics(BaseModel):
    timestamp: str = Field(..., description="时间戳")
    metrics: SystemMetrics = Field(..., description="系统指标")
    performance: PerformanceMetrics = Field(..., description="性能指标")

# 告警相关
class SystemAlert(BaseModel):
    id: int = Field(..., description="告警ID")
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    title: str = Field(..., description="告警标题")
    message: str = Field(..., description="告警消息")
    metric_value: Optional[float] = Field(None, description="指标值")
    threshold_value: Optional[float] = Field(None, description="阈值")
    is_resolved: bool = Field(..., description="是否已解决")
    created_at: str = Field(..., description="创建时间")
    resolved_at: Optional[str] = Field(None, description="解决时间")

class AlertCreate(BaseModel):
    alert_type: str = Field(..., description="告警类型")
    severity: str = Field(..., description="严重程度")
    title: str = Field(..., description="告警标题")
    message: str = Field(..., description="告警消息")
    metric_value: Optional[float] = Field(None, description="指标值")
    threshold_value: Optional[float] = Field(None, description="阈值")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")

# 统计相关
class TimeSeriesData(BaseModel):
    timestamp: str = Field(..., description="时间戳")
    value: float = Field(..., description="数值")
    label: Optional[str] = Field(None, description="标签")

class ChartData(BaseModel):
    labels: List[str] = Field(..., description="标签列表")
    datasets: List[Dict[str, Any]] = Field(..., description="数据集")

class DashboardData(BaseModel):
    system_metrics: SystemMetrics = Field(..., description="系统指标")
    performance_metrics: PerformanceMetrics = Field(..., description="性能指标")
    model_metrics: List[ModelMetrics] = Field(..., description="模型指标")
    recent_logs: List[LogEntry] = Field(..., description="最近日志")
    alerts: List[SystemAlert] = Field(..., description="系统告警")
    charts: Dict[str, ChartData] = Field(..., description="图表数据") 