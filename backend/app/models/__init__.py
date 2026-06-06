from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    followup_records = relationship("FollowupRecord", back_populates="uploaded_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class FollowupTemplate(Base):
    __tablename__ = "followup_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    fields = Column(Text, nullable=False)
    score_min = Column(Float, default=0)
    score_max = Column(Float, default=100)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FollowupRecord(Base):
    __tablename__ = "followup_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    patient_name = Column(String(100))
    template_id = Column(Integer, ForeignKey("followup_templates.id"))
    followup_date = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)
    data = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    batch_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    uploaded_by_user = relationship("User", back_populates="followup_records")
    template = relationship("FollowupTemplate")


class FollowupPlan(Base):
    __tablename__ = "followup_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    patient_name = Column(String(100))
    plan_date = Column(DateTime, nullable=False)
    description = Column(Text)
    status = Column(String(20), default="pending")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    batch_id = Column(String(100), index=True)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class ErrorRecord(Base):
    __tablename__ = "error_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), index=True, nullable=False)
    row_number = Column(Integer, nullable=False)
    patient_id = Column(String(50))
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    row_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), index=True, nullable=False)
    patient_name = Column(String(100))
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    record_id = Column(Integer, ForeignKey("followup_records.id"))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
