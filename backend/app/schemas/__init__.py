from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    fields: str
    score_min: float = 0
    score_max: float = 100
    is_active: bool = True


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[str] = None
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecordBase(BaseModel):
    patient_id: str
    patient_name: Optional[str] = None
    template_id: int
    followup_date: datetime
    score: float
    data: Optional[str] = None


class RecordResponse(RecordBase):
    id: int
    uploaded_by: Optional[int] = None
    batch_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecordWithScoreChange(RecordResponse):
    score_change: Optional[float] = None
    previous_score: Optional[float] = None


class PlanBase(BaseModel):
    patient_id: str
    patient_name: Optional[str] = None
    plan_date: datetime
    description: Optional[str] = None
    status: str = "pending"


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    plan_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PlanResponse(PlanBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ErrorRecordResponse(BaseModel):
    id: int
    batch_id: str
    row_number: int
    patient_id: Optional[str] = None
    error_type: str
    error_message: str
    row_data: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResult(BaseModel):
    batch_id: str
    total_rows: int
    success_count: int
    error_count: int
    errors: List[ErrorRecordResponse]
    success_records: List[RecordResponse]


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    batch_id: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    patient_id: str
    patient_name: Optional[str] = None
    alert_type: str
    message: str
    record_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreTrendItem(BaseModel):
    followup_date: datetime
    score: float
    patient_id: str
    patient_name: Optional[str] = None


class PatientOverview(BaseModel):
    patient_id: str
    patient_name: Optional[str] = None
    total_records: int
    latest_score: Optional[float] = None
    latest_followup_date: Optional[datetime] = None
    score_trend: List[ScoreTrendItem]
    recent_records: List[RecordResponse]
    pending_plans: List[PlanResponse]
    unread_alerts: List[AlertResponse]

    class Config:
        from_attributes = True
