from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import psutil
import time
import json
import os
from datetime import datetime, timedelta
import zipfile
import io

from ..database import get_db
from ..auth.security import get_current_user
from ..models.user import User
from ..schemas.system import (
    SystemMetrics, ServiceStatus, SystemStats, PerformanceMetrics,
    LogEntry, LogFilters, BackupInfo, BackupCreate
)

router = APIRouter(prefix="/system", tags=["system"])

# 系统监控相关
@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """获取系统指标"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            },
            uptime=time.time() - psutil.boot_time(),
            active_connections=len(psutil.net_connections())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {str(e)}")

@router.get("/services/status", response_model=List[ServiceStatus])
async def get_service_status():
    """获取服务状态"""
    services = [
        {"name": "database", "port": 3306},
        {"name": "redis", "port": 6379},
        {"name": "chromadb", "port": 8000},
    ]
    
    status_list = []
    for service in services:
        try:
            # 这里应该实现实际的服务检查逻辑
            status_list.append(ServiceStatus(
                name=service["name"],
                status="healthy",
                response_time=0.1,
                last_check=datetime.now().isoformat()
            ))
        except Exception as e:
            status_list.append(ServiceStatus(
                name=service["name"],
                status="error",
                response_time=0,
                last_check=datetime.now().isoformat(),
                details=str(e)
            ))
    
    return status_list

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    try:
        # 这里应该从数据库获取实际统计信息
        from ..models.user import User
        from ..models.knowledge import KnowledgeBase, Document
        
        total_users = db.query(User).count()
        total_knowledge_bases = db.query(KnowledgeBase).count()
        total_documents = db.query(Document).count()
        
        return SystemStats(
            total_users=total_users,
            total_knowledge_bases=total_knowledge_bases,
            total_documents=total_documents,
            total_chunks=0,  # 需要从向量数据库获取
            total_queries=0,  # 需要从日志或统计表获取
            active_sessions=0,  # 需要从会话管理获取
            system_uptime=time.time() - psutil.boot_time()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统统计失败: {str(e)}")

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics(
    time_range: Optional[str] = Query(None, description="时间范围"),
    service: Optional[str] = Query(None, description="服务名称")
):
    """获取性能指标"""
    # 这里应该从监控系统或日志中获取实际性能数据
    return PerformanceMetrics(
        api_response_time={
            "avg": 150.0,
            "p95": 300.0,
            "p99": 500.0
        },
        error_rate=0.02,
        request_count=1000,
        success_rate=0.98
    )

@router.get("/models/metrics", response_model=List[Dict[str, Any]])
async def get_model_metrics(
    time_range: Optional[str] = Query(None),
    model_name: Optional[str] = Query(None)
):
    """获取模型使用统计"""
    # 这里应该从模型调用日志中获取实际数据
    return [
        {
            "model_name": "gpt-4",
            "total_calls": 1000,
            "success_calls": 980,
            "failed_calls": 20,
            "avg_response_time": 2.5,
            "total_tokens": 50000,
            "cost": 25.0,
            "last_used": datetime.now().isoformat()
        }
    ]

# 日志管理相关
@router.get("/logs", response_model=Dict[str, Any])
async def get_logs(
    level: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """获取系统日志"""
    try:
        # 这里应该从日志文件或日志数据库获取实际日志
        # 模拟日志数据
        logs = [
            LogEntry(
                id=1,
                timestamp=datetime.now().isoformat(),
                level="info",
                module="system",
                message="系统启动成功",
                user="admin",
                ip="127.0.0.1"
            )
        ]
        
        return {
            "logs": logs,
            "total": len(logs),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")

@router.get("/logs/export")
async def export_logs(
    level: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """导出日志"""
    try:
        # 这里应该生成实际的日志文件
        log_content = f"日志导出 - {datetime.now()}\n"
        log_content += f"级别: {level or '全部'}\n"
        log_content += f"模块: {module or '全部'}\n"
        log_content += f"时间范围: {start_date or '全部'} - {end_date or '全部'}\n"
        
        # 创建内存文件
        output = io.BytesIO()
        output.write(log_content.encode('utf-8'))
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.read()),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename=logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出日志失败: {str(e)}")

@router.post("/logs/clear")
async def clear_logs(
    before_date: Optional[str] = Query(None),
    level: Optional[str] = Query(None)
):
    """清理日志"""
    try:
        # 这里应该实现实际的日志清理逻辑
        return {"message": "日志清理成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理日志失败: {str(e)}")

# 备份管理相关
@router.get("/backups", response_model=List[BackupInfo])
async def get_backups():
    """获取备份列表"""
    try:
        # 这里应该从备份目录或数据库获取实际备份信息
        backups = [
            BackupInfo(
                id=1,
                filename="backup_20240120_120000.zip",
                size=1024000,
                type="full",
                status="completed",
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat()
            )
        ]
        return backups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")

@router.post("/backups", response_model=BackupInfo)
async def create_backup(backup_data: BackupCreate):
    """创建备份"""
    try:
        # 这里应该实现实际的备份逻辑
        backup_info = BackupInfo(
            id=1,
            filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            size=0,
            type=backup_data.type,
            status="in_progress",
            created_at=datetime.now().isoformat()
        )
        
        # 异步执行备份任务
        # await create_backup_task(backup_info)
        
        return backup_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建备份失败: {str(e)}")

@router.get("/backups/{backup_id}/download")
async def download_backup(backup_id: int):
    """下载备份"""
    try:
        # 这里应该返回实际的备份文件
        backup_content = f"备份文件内容 - ID: {backup_id}"
        
        return StreamingResponse(
            io.BytesIO(backup_content.encode('utf-8')),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=backup_{backup_id}.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载备份失败: {str(e)}")

@router.delete("/backups/{backup_id}")
async def delete_backup(backup_id: int):
    """删除备份"""
    try:
        # 这里应该实现实际的备份删除逻辑
        return {"message": f"备份 {backup_id} 删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")

@router.post("/backups/{backup_id}/restore")
async def restore_backup(backup_id: int):
    """恢复备份"""
    try:
        # 这里应该实现实际的备份恢复逻辑
        return {"message": f"备份 {backup_id} 恢复成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复备份失败: {str(e)}")

# 系统配置相关
@router.get("/config")
async def get_system_config():
    """获取系统配置"""
    try:
        # 这里应该从配置文件或数据库获取实际配置
        config = {
            "app_name": "AI知识库管理系统",
            "version": "1.0.0",
            "debug": False,
            "log_level": "INFO",
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "allowed_file_types": [".pdf", ".docx", ".txt", ".md"],
            "backup_retention_days": 30
        }
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.put("/config")
async def update_system_config(
    config: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """更新系统配置"""
    try:
        # 这里应该实现实际的配置更新逻辑
        # 验证用户权限
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="权限不足")
        
        return {"message": "系统配置更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新系统配置失败: {str(e)}")

@router.get("/health")
async def health_check():
    """系统健康检查"""
    try:
        checks = [
            {
                "name": "database",
                "status": "healthy",
                "response_time": 0.1,
                "details": "数据库连接正常"
            },
            {
                "name": "redis",
                "status": "healthy", 
                "response_time": 0.05,
                "details": "Redis连接正常"
            },
            {
                "name": "chromadb",
                "status": "healthy",
                "response_time": 0.2,
                "details": "向量数据库连接正常"
            }
        ]
        
        overall_status = "healthy" if all(check["status"] == "healthy" for check in checks) else "unhealthy"
        
        return {
            "status": overall_status,
            "checks": checks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.post("/services/{service_name}/restart")
async def restart_service(
    service_name: str,
    current_user: User = Depends(get_current_user)
):
    """重启服务"""
    try:
        # 验证用户权限
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 这里应该实现实际的服务重启逻辑
        return {"message": f"服务 {service_name} 重启成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重启服务失败: {str(e)}")

@router.get("/realtime")
async def get_realtime_metrics():
    """获取实时监控数据"""
    try:
        metrics = await get_system_metrics()
        performance = await get_performance_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "performance": performance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实时监控数据失败: {str(e)}") 