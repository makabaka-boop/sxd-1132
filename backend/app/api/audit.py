from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, ErrorRecord, AuditLog, Alert
from ..schemas import ErrorRecordResponse, AuditLogResponse, AlertResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter()


@router.get("/errors/batch/{batch_id}", response_model=List[ErrorRecordResponse])
def get_batch_errors(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "auditor", "user"]))
):
    errors = db.query(ErrorRecord).filter(
        ErrorRecord.batch_id == batch_id
    ).order_by(ErrorRecord.row_number.asc()).all()
    return errors


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "auditor"]))
):
    logs = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    return logs


@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    is_read: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = db.query(Alert).filter(
        Alert.is_read == is_read
    ).order_by(Alert.created_at.desc()).all()
    return alerts


@router.put("/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()
    return {"message": "已标记为已读"}
