"""
Locked Takeoff Schemas - Descriptions locked from database
"""

from __future__ import annotations
from typing import Optional, List
from decimal import Decimal
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class LaborMode(str, Enum):
    auto = "auto"
    manual = "manual"

class Operation(str, Enum):
    PRESSBRAKE_FORMING = "Pressbrake Forming"
    ROLL_FORMING = "Roll Forming" 
    SAW_CUTTING = "Saw Cutting"
    DRILL_PUNCH = "Drill & Punch"
    DRAGON_PLASMA_CUTTING = "Dragon Plasma Cutting"
    BEAM_LINE_CUTTING = "Beam Line Cutting"
    SHEARING = "Shearing"

class CoatingSystem(str, Enum):
    SHOP_COATING = "Shop Coating"
    EPOXY = "Epoxy"
    POWDER_COAT = "Powder Coat" 
    GALVANIZED = "Galvanized"
    NONE = "None"

class TakeoffCalculationRequest(BaseModel):
    qty: int = Field(..., ge=1)
    shape_key: str = Field(..., min_length=1, description="Material shape key")
    length_ft: Decimal = Field(..., ge=Decimal('0'))
    width_ft: Optional[Decimal] = Field(None, ge=Decimal('0'))
    unit_price_per_cwt: Optional[Decimal] = Field(None, ge=Decimal('0'))
    calculate_labor: bool = Field(True)
    labor_mode: Optional[LaborMode] = Field(LaborMode.auto)
    operations: Optional[List[Operation]] = None
    coatings_selected: Optional[List[CoatingSystem]] = None
    primary_coating: Optional[str] = None
    secondary_coating: Optional[str] = None

class TakeoffCalculationResponse(BaseModel):
    qty: int
    shape_key: str
    description: str  # LOCKED from database
    category: str
    length_ft: Decimal
    width_ft: Optional[Decimal] = None
    weight_per_ft: Decimal
    unit_price_per_cwt: Decimal
    total_length_ft: Decimal
    total_weight_lbs: Decimal
    total_weight_tons: Decimal
    total_price: Decimal
    labor_hours: Optional[Decimal] = None
    labor_rate: Optional[Decimal] = None
    labor_cost: Optional[Decimal] = None
    labor_mode: Optional[str] = None
    coating_cost: Optional[Decimal] = None
    coating_details: Optional[str] = None
    material_confirmed: bool = True  # Always true in locked mode

class TakeoffEntryCreate(BaseModel):
    qty: int = Field(..., ge=1)
    shape_key: str = Field(..., min_length=1)
    # description is NOT included - locked from database
    length_ft: Decimal = Field(..., ge=Decimal('0'))
    width_ft: Optional[Decimal] = Field(None, ge=Decimal('0'))
    thickness_in: Optional[Decimal] = Field(None, ge=Decimal('0'))
    labor_mode: Optional[LaborMode] = Field(LaborMode.auto)
    operations: Optional[List[Operation]] = None
    coatings_selected: Optional[List[CoatingSystem]] = None
    primary_coating: Optional[str] = None
    secondary_coating: Optional[str] = None

class TakeoffEntryUpdate(BaseModel):
    qty: Optional[int] = Field(None, ge=1)
    shape_key: Optional[str] = Field(None, min_length=1)
    # description is NOT included - locked from database
    length_ft: Optional[Decimal] = Field(None, ge=Decimal('0'))
    width_ft: Optional[Decimal] = Field(None, ge=Decimal('0'))
    labor_mode: Optional[LaborMode] = None
    operations: Optional[List[Operation]] = None
    coatings_selected: Optional[List[CoatingSystem]] = None
    primary_coating: Optional[str] = None
    secondary_coating: Optional[str] = None

class TakeoffEntryResponse(BaseModel):
    id: Optional[int]
    qty: int
    shape_key: str
    description: str  # LOCKED from database
    category: Optional[str]
    length_ft: Decimal
    width_ft: Optional[Decimal]
    weight_per_ft: Decimal
    total_length_ft: Decimal
    total_weight_lbs: Decimal
    total_weight_tons: Decimal
    unit_price_per_cwt: Decimal
    total_price: Decimal
    labor_hours: Optional[Decimal]
    labor_rate: Optional[Decimal]
    labor_cost: Optional[Decimal]
    labor_mode: Optional[str]
    operations: Optional[List[str]]
    coatings_selected: Optional[List[str]]
    primary_coating: Optional[str]
    secondary_coating: Optional[str]
    coating_cost: Optional[Decimal]
    created_at: Optional[datetime]
    material_confirmed: Optional[bool] = True

    class Config:
        from_attributes = True

class ProjectTotalsResponse(BaseModel):
    total_entries: int
    total_length_ft: Decimal
    total_weight_lbs: Decimal
    total_weight_tons: Decimal
    total_material_cost: Decimal
    total_labor_hours: Decimal
    total_labor_cost: Decimal
    total_coating_cost: Decimal
    total_project_cost: Decimal