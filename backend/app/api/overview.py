from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import User, FollowupRecord, FollowupPlan, Alert
from ..schemas import PatientOverview
from ..utils.auth import get_current_user

router = APIRouter()


@router.get("/patient/{patient_id}", response_model=PatientOverview)
def get_patient_overview(
    patient_id: str,
    recent_limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(FollowupRecord).filter(
        FollowupRecord.patient_id == patient_id
    ).order_by(FollowupRecord.followup_date.desc()).all()

    latest_score = records[0].score if records else None
    latest_followup_date = records[0].followup_date if records else None
    patient_name = records[0].patient_name if records else None

    score_trend = []
    for record in sorted(records, key=lambda r: r.followup_date):
        score_trend.append({
            "followup_date": record.followup_date,
            "score": record.score,
            "patient_id": patient_id,
            "patient_name": patient_name
        })

    recent_records = records[:recent_limit]

    pending_plans = db.query(FollowupPlan).filter(
        FollowupPlan.patient_id == patient_id,
        FollowupPlan.status == "pending"
    ).order_by(FollowupPlan.plan_date.asc()).all()

    unread_alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id,
        Alert.is_read == False
    ).order_by(Alert.created_at.desc()).all()

    return PatientOverview(
        patient_id=patient_id,
        patient_name=patient_name,
        total_records=len(records),
        latest_score=latest_score,
        latest_followup_date=latest_followup_date,
        score_trend=score_trend,
        recent_records=recent_records,
        pending_plans=pending_plans,
        unread_alerts=unread_alerts
    )
