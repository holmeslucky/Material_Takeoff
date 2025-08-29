from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.template import Template

router = APIRouter()

# Pydantic models
class TemplateCreate(BaseModel):
    name: str
    category: str = Field(..., pattern="^(Main Takeoff|Ductwork Takeoff|Pipe Takeoff)$")
    description: Optional[str] = None
    items: List[dict] = []
    calculator_settings: Optional[dict] = {}

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(Main Takeoff|Ductwork Takeoff|Pipe Takeoff)$")
    description: Optional[str] = None
    items: Optional[List[dict]] = None
    calculator_settings: Optional[dict] = None

class TemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str]
    items: List[dict]
    calculator_settings: Optional[dict]
    created_date: datetime
    modified_date: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TemplateResponse])
def get_templates(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all templates, optionally filtered by category"""
    query = db.query(Template)
    
    if category and category != "all":
        query = query.filter(Template.category == category)
    
    templates = query.order_by(Template.modified_date.desc()).all()
    return templates

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template by ID"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template

@router.post("/", response_model=TemplateResponse)
def create_template(template_data: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template"""
    template = Template(
        name=template_data.name,
        category=template_data.category,
        description=template_data.description,
        items=template_data.items,
        calculator_settings=template_data.calculator_settings or {}
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: str, 
    template_data: TemplateUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update fields that were provided
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete a template"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}

@router.post("/{template_id}/duplicate", response_model=TemplateResponse)
def duplicate_template(template_id: str, db: Session = Depends(get_db)):
    """Create a duplicate of an existing template"""
    original = db.query(Template).filter(Template.id == template_id).first()
    if not original:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Create a new template with copied data
    duplicate = Template(
        name=f"{original.name} (Copy)",
        category=original.category,
        description=original.description,
        items=original.items.copy() if original.items else [],
        calculator_settings=original.calculator_settings.copy() if original.calculator_settings else {}
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    return duplicate