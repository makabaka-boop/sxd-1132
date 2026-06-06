from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, FollowupTemplate
from ..schemas import TemplateCreate, TemplateUpdate, TemplateResponse
from ..utils.auth import get_current_user, require_role

router = APIRouter()


@router.get("/", response_model=List[TemplateResponse])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = db.query(FollowupTemplate).filter(
        FollowupTemplate.is_active == True
    ).offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    template = db.query(FollowupTemplate).filter(FollowupTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.post("/", response_model=TemplateResponse)
def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    template = FollowupTemplate(
        **template_data.model_dump(),
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    template = db.query(FollowupTemplate).filter(FollowupTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    update_data = template_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    template = db.query(FollowupTemplate).filter(FollowupTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    template.is_active = False
    db.commit()
    return {"message": "模板已删除"}
