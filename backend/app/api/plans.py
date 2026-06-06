from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import User, FollowupPlan
from ..schemas import PlanCreate, PlanUpdate, PlanResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter()


@router.get("/", response_model=List[PlanResponse])
def list_plans(
    patient_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FollowupPlan)

    if patient_id:
        query = query.filter(FollowupPlan.patient_id == patient_id)
    if status:
        query = query.filter(FollowupPlan.status == status)

    plans = query.order_by(FollowupPlan.plan_date.asc()).offset(skip).limit(limit).all()
    return plans


@router.post("/", response_model=PlanResponse)
def create_plan(
    plan_data: PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "user"]))
):
    plan = FollowupPlan(
        **plan_data.model_dump(),
        created_by=current_user.id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "user"]))
):
    plan = db.query(FollowupPlan).filter(FollowupPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    update_data = plan_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    plan = db.query(FollowupPlan).filter(FollowupPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    db.delete(plan)
    db.commit()
    return {"message": "计划已删除"}
