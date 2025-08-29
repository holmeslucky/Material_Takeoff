
from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.takeoff import TakeoffEntry
from app.models.material import Material
from app.services.takeoff_service import TakeoffCalculationService
from app.schemas.takeoff_schemas_locked import (
    TakeoffEntryCreate, TakeoffEntryUpdate, TakeoffEntryResponse,
    TakeoffCalculationRequest, TakeoffCalculationResponse,
    ProjectTotalsResponse, LaborMode
)

router = APIRouter()
svc = TakeoffCalculationService()

def _material_or_400(db: Session, shape_key: str) -> Material:
    mat = db.query(Material).filter(Material.shape_key == shape_key.upper()).first()
    if not mat:
        raise HTTPException(status_code=400, detail="Shape not found in Materials catalog")
    return mat

@router.post("/calculate", response_model=TakeoffCalculationResponse)
async def calculate_takeoff_entry(request: TakeoffCalculationRequest, db: Session = Depends(get_db)):
    mat = db.query(Material).filter(Material.shape_key == request.shape_key.upper()).first()
    material_confirmed = bool(mat)
    calc = svc.calculate_entry(
        qty=request.qty,
        shape_key=request.shape_key,
        length_ft=request.length_ft,
        width_ft=request.width_ft or 0,
        material_data=mat,
        unit_price_per_cwt=request.unit_price_per_cwt,
    )
    if request.calculate_labor:
        labor = svc.calculate_labor_hours(
            material_key=request.shape_key,
            qty=request.qty,
            length_ft=request.length_ft,
            mode=request.labor_mode.value if isinstance(request.labor_mode, LaborMode) else (request.labor_mode or "auto"),
        )
        calc.update(labor)
    if hasattr(svc, "calculate_coatings"):
        coat_res = svc.calculate_coatings(
            material_key=request.shape_key,
            qty=request.qty,
            length_ft=request.length_ft,
            width_ft=request.width_ft or 0,
            total_weight_lbs=calc.get("total_weight_lbs"),
            primary=request.primary_coating,
        )
        calc.update(coat_res)
    calc["material_confirmed"] = material_confirmed
    if mat:
        calc["description"] = mat.description
        calc["category"] = getattr(mat, "category", calc.get("category", "Other"))
    return TakeoffCalculationResponse(**calc)

@router.get("/projects/{project_id}/entries", response_model=List[TakeoffEntryResponse])
async def get_project_takeoff_entries(project_id: str, db: Session = Depends(get_db)):
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).order_by(TakeoffEntry.created_at).all()
    for e in entries:
        setattr(e, "material_confirmed", True)
    return entries

@router.post("/projects/{project_id}/entries", response_model=TakeoffEntryResponse, status_code=201)
async def create_takeoff_entry(project_id: str, entry_data: TakeoffEntryCreate, db: Session = Depends(get_db)):
    mat = _material_or_400(db, entry_data.shape_key)
    req = TakeoffCalculationRequest(
        qty=entry_data.qty,
        shape_key=entry_data.shape_key,
        length_ft=entry_data.length_ft,
        width_ft=entry_data.width_ft,
        unit_price_per_cwt=None,
        calculate_labor=True,
        labor_mode=entry_data.labor_mode,
        primary_coating=entry_data.primary_coating,
    )
    calc = await calculate_takeoff_entry(req, db)
    db_entry = TakeoffEntry(
        project_id=project_id,
        qty=entry_data.qty,
        shape_key=entry_data.shape_key.upper(),
        description=mat.description,
        length_ft=entry_data.length_ft,
        width_ft=entry_data.width_ft or 0.0,
        weight_per_ft=calc.weight_per_ft,
        total_length_ft=calc.total_length_ft,
        total_weight_lbs=calc.total_weight_lbs,
        total_weight_tons=calc.total_weight_tons,
        unit_price_per_cwt=calc.unit_price_per_cwt,
        total_price=calc.total_price,
        labor_hours=getattr(calc, "labor_hours", None),
        labor_rate=getattr(calc, "labor_rate", None),
        labor_cost=getattr(calc, "labor_cost", None),
        labor_mode=entry_data.labor_mode.value if hasattr(entry_data.labor_mode, "value") else entry_data.labor_mode,
        primary_coating=entry_data.primary_coating,
        coating_cost=getattr(calc, "coating_cost", None),
        coating_details=getattr(calc, "coating_details", None),
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    setattr(db_entry, "material_confirmed", True)
    return db_entry

@router.put("/entries/{entry_id}", response_model=TakeoffEntryResponse)
async def update_takeoff_entry(entry_id: int, entry_update: TakeoffEntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(TakeoffEntry).filter(TakeoffEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Takeoff entry not found")
    if entry_update.shape_key is not None:
        mat = _material_or_400(db, entry_update.shape_key)
        db_entry.shape_key = entry_update.shape_key.upper()
        db_entry.description = mat.description
    up = entry_update.dict(exclude_unset=True)
    up.pop("description", None)
    for field in ("qty", "length_ft", "width_ft", "labor_mode", "primary_coating"):
        if field in up and up[field] is not None:
            setattr(db_entry, field, up[field])
    req = TakeoffCalculationRequest(
        qty=db_entry.qty,
        shape_key=db_entry.shape_key,
        length_ft=db_entry.length_ft,
        width_ft=db_entry.width_ft,
        unit_price_per_cwt=None,
        calculate_labor=True,
        labor_mode=db_entry.labor_mode,
        primary_coating=getattr(db_entry, "primary_coating", None),
    )
    calc = await calculate_takeoff_entry(req, db)
    db_entry.weight_per_ft = calc.weight_per_ft
    db_entry.total_length_ft = calc.total_length_ft
    db_entry.total_weight_lbs = calc.total_weight_lbs
    db_entry.total_weight_tons = calc.total_weight_tons
    db_entry.unit_price_per_cwt = calc.unit_price_per_cwt
    db_entry.total_price = calc.total_price
    db_entry.labor_hours = getattr(calc, "labor_hours", None)
    db_entry.labor_rate = getattr(calc, "labor_rate", None)
    db_entry.labor_cost = getattr(calc, "labor_cost", None)
    db_entry.coating_cost = getattr(calc, "coating_cost", None)
    db_entry.coating_details = getattr(calc, "coating_details", None)
    db.commit()
    db.refresh(db_entry)
    setattr(db_entry, "material_confirmed", True)
    return db_entry

@router.get("/projects/{project_id}/totals", response_model=ProjectTotalsResponse)
async def get_project_totals(project_id: str, db: Session = Depends(get_db)):
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
    entry_dicts = []
    for e in entries:
        entry_dicts.append({
            'total_length_ft': e.total_length_ft,
            'total_weight_lbs': e.total_weight_lbs,
            'total_weight_tons': e.total_weight_tons,
            'total_price': e.total_price,
            'labor_hours': e.labor_hours or 0,
            'labor_cost': e.labor_cost or 0,
            'coating_cost': getattr(e, 'coating_cost', 0) or 0,
            'category': e.material.category if getattr(e, 'material', None) else 'Other',
        })
    totals = svc.calculate_project_totals(entry_dicts)
    return ProjectTotalsResponse(**totals)
