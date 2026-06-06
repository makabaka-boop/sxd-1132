from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, FollowupRecord, FollowupTemplate
from ..schemas import UploadResult, RecordResponse, RecordWithScoreChange
from ..utils.auth import get_current_user, require_role
from ..utils.validator import process_upload_file

router = APIRouter()


@router.post("/upload", response_model=UploadResult)
async def upload_records(
    file: UploadFile = File(...),
    template_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "user"]))
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="请上传文件")

    content = await file.read()
    try:
        result = process_upload_file(content, file.filename, template_id, current_user.id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[RecordResponse])
def list_records(
    patient_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FollowupRecord)

    if patient_id:
        query = query.filter(FollowupRecord.patient_id == patient_id)
    if start_date:
        query = query.filter(FollowupRecord.followup_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(FollowupRecord.followup_date <= datetime.strptime(end_date, '%Y-%m-%d'))

    records = query.order_by(FollowupRecord.followup_date.desc()).offset(skip).limit(limit).all()
    return records


@router.get("/patient/{patient_id}/score-changes", response_model=List[RecordWithScoreChange])
def get_patient_score_changes(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(FollowupRecord).filter(
        FollowupRecord.patient_id == patient_id
    ).order_by(FollowupRecord.followup_date.asc()).all()

    result = []
    previous_score = None
    for record in records:
        record_dict = RecordWithScoreChange.model_validate(record).model_dump()
        if previous_score is not None:
            record_dict['score_change'] = record.score - previous_score
            record_dict['previous_score'] = previous_score
        previous_score = record.score
        result.append(RecordWithScoreChange(**record_dict))

    return result


@router.get("/batch/{batch_id}", response_model=List[RecordResponse])
def get_batch_records(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(FollowupRecord).filter(
        FollowupRecord.batch_id == batch_id
    ).all()
    return records
