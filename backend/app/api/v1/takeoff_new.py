
"""
Variant of the takeoff router that passes `operations` and `coatings_selected` into calculations.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.material import Material
from app.models.takeoff import TakeoffEntry
from app.schemas.takeoff_schemas import (
    TakeoffEntryCreate, TakeoffEntryUpdate, TakeoffEntryResponse,
    TakeoffCalculationRequest, TakeoffCalculationResponse,
    ProjectTotalsResponse
)
from app.services.takeoff_service import TakeoffCalculationService

router = APIRouter()
svc = TakeoffCalculationService()

@router.post("/calculate", response_model=TakeoffCalculationResponse)
async def calculate(request: TakeoffCalculationRequest, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.shape_key == request.shape_key.upper()).first()
    result = svc.calculate_entry(
        qty=request.qty,
        shape_key=request.shape_key,
        length_ft=request.length_ft,
        width_ft=request.width_ft or 0.0,
        material_data=material,
        unit_price_per_cwt=request.unit_price_per_cwt,
    )
    # labor
    if request.calculate_labor:
        labor = svc.calculate_labor_hours(
            material_key=request.shape_key,
            qty=request.qty,
            length_ft=request.length_ft,
            mode=(request.labor_mode or "auto"),
            operations=[op.value if hasattr(op, "value") else op for op in (request.operations or [])],
        )
        result.update(labor)
    # coatings
    coats = svc.calculate_coatings(
        material_key=request.shape_key,
        qty=request.qty,
        length_ft=request.length_ft,
        width_ft=request.width_ft or 0.0,
        total_weight_lbs=result.get("total_weight_lbs"),
        coatings_selected=[c.value if hasattr(c, "value") else c for c in (request.coatings_selected or [])],
        primary=request.primary_coating,
        secondary=request.secondary_coating,
    )
    result.update(coats)
    return TakeoffCalculationResponse(**result)

@router.post("/projects/{project_id}/entries", response_model=TakeoffEntryResponse, status_code=201)
async def create_entry(project_id: str, data: TakeoffEntryCreate, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.shape_key == data.shape_key.upper()).first()
    # calc
    req = TakeoffCalculationRequest(
        qty=data.qty,
        shape_key=data.shape_key,
        length_ft=data.length_ft,
        width_ft=data.width_ft,
        unit_price_per_cwt=None,
        calculate_labor=True,
        labor_mode=data.labor_mode,
        operations=data.operations,
        primary_coating=data.primary_coating,
        secondary_coating=data.secondary_coating,
        coatings_selected=data.coatings_selected,
    )
    calc = await calculate(req, db)  # reuse endpoint logic
    # Persist
    entry_kwargs = dict(
        project_id=project_id,
        qty=data.qty,
        shape_key=data.shape_key.upper(),
        description=calc.description,
        length_ft=data.length_ft,
        width_ft=data.width_ft or 0.0,
        weight_per_ft=calc.weight_per_ft,
        total_length_ft=calc.total_length_ft,
        total_weight_lbs=calc.total_weight_lbs,
        total_weight_tons=calc.total_weight_tons,
        unit_price_per_cwt=calc.unit_price_per_cwt,
        total_price=calc.total_price,
        labor_hours=getattr(calc, "labor_hours", None),
        labor_rate=getattr(calc, "labor_rate", None),
        labor_cost=getattr(calc, "labor_cost", None),
        labor_mode=getattr(data, "labor_mode", None),
        primary_coating=getattr(data, "primary_coating", None),
        secondary_coating=getattr(data, "secondary_coating", None),
        coating_cost=getattr(calc, "coating_cost", None),
        coating_details=getattr(calc, "coating_details", None),
    )
    # Optional JSON columns
    if hasattr(TakeoffEntry, "operations_selected"):
        entry_kwargs["operations_selected"] = [op.value if hasattr(op, "value") else op for op in (data.operations or [])]
    if hasattr(TakeoffEntry, "coatings_selected"):
        entry_kwargs["coatings_selected"] = [c.value if hasattr(c, "value") else c for c in (data.coatings_selected or [])]

    entry = TakeoffEntry(**entry_kwargs)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
