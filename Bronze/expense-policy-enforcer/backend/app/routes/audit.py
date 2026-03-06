"""
Audit log routes - View and export audit trail
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import AuditLog
from app.schemas import AuditLogResponse

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    expense_id: str = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List audit logs with optional filtering"""
    query = select(AuditLog).order_by(AuditLog.timestamp.desc())
    
    if expense_id:
        query = query.where(AuditLog.expense_id == expense_id)
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return logs


@router.get("/stats")
async def get_audit_stats(db: AsyncSession = Depends(get_db)):
    """Get audit log statistics"""
    # Total logs
    total = await db.execute(select(func.count(AuditLog.id)))
    total_count = total.scalar() or 0
    
    # Logs by action
    actions = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
    )
    action_counts = {row[0]: row[1] for row in action.all()}
    
    return {
        "total_logs": total_count,
        "by_action": action_counts
    }
