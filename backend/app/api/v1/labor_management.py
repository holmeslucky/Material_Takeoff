"""
Labor Management API - CRUD operations for labor operations, coating systems, and settings
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.labor_operation import LaborOperation
from app.models.coating_system import CoatingSystem  
from app.models.labor_settings import LaborSettings
from app.schemas.labor import (
    LaborOperationCreate, LaborOperationUpdate, LaborOperationResponse,
    CoatingSystemCreate, CoatingSystemUpdate, CoatingSystemResponse,
    LaborSettingsCreate, LaborSettingsUpdate, LaborSettingsResponse
)

router = APIRouter()

# ======= LABOR OPERATIONS CRUD =======
@router.get("/operations", response_model=List[LaborOperationResponse])
async def get_labor_operations(db: Session = Depends(get_db)):
    """Get all labor operations"""
    operations = db.query(LaborOperation).filter(LaborOperation.active == True).order_by(LaborOperation.name).all()
    return operations

@router.post("/operations", response_model=LaborOperationResponse, status_code=201)
async def create_labor_operation(operation: LaborOperationCreate, db: Session = Depends(get_db)):
    """Create a new labor operation"""
    # Check for duplicate name
    existing = db.query(LaborOperation).filter(LaborOperation.name == operation.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Labor operation '{operation.name}' already exists")
    
    db_operation = LaborOperation(**operation.dict())
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation

@router.put("/operations/{operation_id}", response_model=LaborOperationResponse)
async def update_labor_operation(operation_id: int, operation: LaborOperationUpdate, db: Session = Depends(get_db)):
    """Update an existing labor operation"""
    db_operation = db.query(LaborOperation).filter(LaborOperation.id == operation_id).first()
    if not db_operation:
        raise HTTPException(status_code=404, detail="Labor operation not found")
    
    # Check for duplicate name if name is being changed
    if operation.name and operation.name != db_operation.name:
        existing = db.query(LaborOperation).filter(LaborOperation.name == operation.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Labor operation '{operation.name}' already exists")
    
    update_data = operation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_operation, field, value)
    
    db.commit()
    db.refresh(db_operation)
    return db_operation

@router.delete("/operations/{operation_id}")
async def delete_labor_operation(operation_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a labor operation"""
    db_operation = db.query(LaborOperation).filter(LaborOperation.id == operation_id).first()
    if not db_operation:
        raise HTTPException(status_code=404, detail="Labor operation not found")
    
    db_operation.active = False
    db.commit()
    return {"message": f"Labor operation '{db_operation.name}' deactivated successfully"}

# ======= COATING SYSTEMS CRUD =======
@router.get("/coatings", response_model=List[CoatingSystemResponse])
async def get_coating_systems(db: Session = Depends(get_db)):
    """Get all coating systems"""
    coatings = db.query(CoatingSystem).filter(CoatingSystem.active == True).order_by(CoatingSystem.name).all()
    return coatings

@router.post("/coatings", response_model=CoatingSystemResponse, status_code=201)
async def create_coating_system(coating: CoatingSystemCreate, db: Session = Depends(get_db)):
    """Create a new coating system"""
    # Check for duplicate name
    existing = db.query(CoatingSystem).filter(CoatingSystem.name == coating.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Coating system '{coating.name}' already exists")
    
    db_coating = CoatingSystem(**coating.dict())
    db.add(db_coating)
    db.commit()
    db.refresh(db_coating)
    return db_coating

@router.put("/coatings/{coating_id}", response_model=CoatingSystemResponse)
async def update_coating_system(coating_id: int, coating: CoatingSystemUpdate, db: Session = Depends(get_db)):
    """Update an existing coating system"""
    db_coating = db.query(CoatingSystem).filter(CoatingSystem.id == coating_id).first()
    if not db_coating:
        raise HTTPException(status_code=404, detail="Coating system not found")
    
    # Check for duplicate name if name is being changed
    if coating.name and coating.name != db_coating.name:
        existing = db.query(CoatingSystem).filter(CoatingSystem.name == coating.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Coating system '{coating.name}' already exists")
    
    update_data = coating.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_coating, field, value)
    
    db.commit()
    db.refresh(db_coating)
    return db_coating

@router.delete("/coatings/{coating_id}")
async def delete_coating_system(coating_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a coating system"""
    db_coating = db.query(CoatingSystem).filter(CoatingSystem.id == coating_id).first()
    if not db_coating:
        raise HTTPException(status_code=404, detail="Coating system not found")
    
    db_coating.active = False
    db.commit()
    return {"message": f"Coating system '{db_coating.name}' deactivated successfully"}

# ======= LABOR SETTINGS CRUD =======
@router.get("/settings", response_model=List[LaborSettingsResponse])
async def get_labor_settings(db: Session = Depends(get_db)):
    """Get all labor settings"""
    settings = db.query(LaborSettings).order_by(LaborSettings.setting_key).all()
    return settings

@router.put("/settings/{setting_key}", response_model=LaborSettingsResponse)
async def update_labor_setting(setting_key: str, setting: LaborSettingsUpdate, db: Session = Depends(get_db)):
    """Update a labor setting value"""
    db_setting = db.query(LaborSettings).filter(LaborSettings.setting_key == setting_key).first()
    if not db_setting:
        raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found")
    
    update_data = setting.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_setting, field, value)
    
    db.commit()
    db.refresh(db_setting)
    return db_setting