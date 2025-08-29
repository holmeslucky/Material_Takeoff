"""
Capitol Engineering Company - Takeoff Schemas
Pydantic models for takeoff API requests and responses
"""

from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class Operation(str, Enum):
    pressbrake_forming = "Pressbrake Forming"
    roll_forming = "Roll Forming"
    saw_cutting = "Saw Cutting"
    drill_punch = "Drill & Punch"
    dragon_plasma_cutting = "Dragon Plasma Cutting"
    beam_line_cutting = "Beam Line Cutting"
    shearing = "Shearing"

class CoatingSystem(str, Enum):
    shop_coating = "Shop Coating"
    epoxy = "Epoxy"
    powder_coat = "Powder Coat"
    galvanized = "Galvanized"
    none = "None"

class TakeoffCalculationRequest(BaseModel):
    """Request for real-time takeoff calculation"""
    qty: int = Field(..., ge=1, description="Quantity of materials")
    shape_key: str = Field(..., min_length=1, description="Material shape key (e.g., W12X26)")
    length_ft: float = Field(..., ge=0, description="Length in feet")
    length_in: Optional[float] = Field(0, ge=0, description="Length in inches (for plates)")
    width_in: Optional[float] = Field(0, ge=0, description="Width in inches (for plates)")
    thickness_in: Optional[float] = Field(0, ge=0, description="Thickness in inches (for plates)")
    unit_price_per_cwt: Optional[float] = Field(None, ge=0, description="Override unit price per CWT")
    calculate_labor: bool = Field(True, description="Include labor calculations")
    labor_mode: Optional[str] = Field("auto", description="Labor calculation mode: auto or manual")
    operations: Optional[List[Operation]] = Field(default_factory=list, description="Selected labor operations (checkboxes)")
    coatings_selected: Optional[List[CoatingSystem]] = Field(default_factory=list, description="Selected coating systems (checkboxes)")
    primary_coating: Optional[str] = None

class TakeoffCalculationResponse(BaseModel):
    """Response from takeoff calculation"""
    # Input values
    qty: int
    shape_key: str
    description: str
    length_ft: float
    length_in: Optional[float] = 0
    width_in: Optional[float] = 0
    thickness_in: Optional[float] = 0
    
    # Material properties
    weight_per_ft: float
    unit_price_per_cwt: float
    category: str
    
    # Calculated values
    total_length_ft: float
    total_weight_lbs: float
    total_weight_tons: float
    total_price: float
    
    # Labor calculations
    labor_hours: Optional[float] = None
    labor_rate: Optional[float] = None
    labor_cost: Optional[float] = None
    labor_mode: Optional[str] = None
    
    # Coating calculations
    coating_cost: Optional[float] = None
    coating_details: Optional[Dict[str, Any]] = None
    
    # Material validation
    material_confirmed: bool = False

class TakeoffEntryBase(BaseModel):
    """Base schema for takeoff entries"""
    qty: int = Field(..., ge=1)
    shape_key: str = Field(..., min_length=1)
    operations: List[Operation] = Field(default_factory=list, description="Selected labor operations (checkboxes)")
    primary_coating: Optional[str] = None
    coatings_selected: List[CoatingSystem] = Field(default_factory=list, description="Selected coating systems (checkboxes)")
    description: str = Field("")
    length_ft: float = Field(..., ge=0)
    width_ft: float = Field(0, ge=0)
    thickness_in: Optional[float] = Field(0, ge=0, description="Thickness in inches (for plates)")
    labor_mode: str = Field("auto")
    coating_cost: Optional[float] = Field(0, ge=0, description="Calculated coating cost")
    notes: Optional[str] = Field("", description="Additional notes")

class TakeoffEntryCreate(TakeoffEntryBase):
    """Schema for creating takeoff entries"""
    pass

class TakeoffEntryUpdate(BaseModel):
    """Schema for updating takeoff entries"""
    qty: Optional[int] = Field(None, ge=1)
    shape_key: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    length_ft: Optional[float] = Field(None, ge=0)
    width_ft: Optional[float] = Field(None, ge=0)
    labor_mode: Optional[str] = None

class TakeoffEntryResponse(TakeoffEntryBase):
    """Schema for takeoff entry responses"""
    id: int
    project_id: str
    
    # Material properties
    weight_per_ft: float
    unit_price_per_cwt: float
    
    # Calculated values
    total_length_ft: float
    total_weight_lbs: float
    total_weight_tons: float
    total_price: float
    
    # Labor calculations
    labor_hours: Optional[float] = None
    labor_rate: Optional[float] = None
    labor_cost: Optional[float] = None
    
    # Labor operations and coatings (from the database)
    operations: Optional[List[Operation]] = Field(default_factory=list)
    coatings_selected: Optional[List[CoatingSystem]] = Field(default_factory=list)
    primary_coating: Optional[str] = None
    coating_cost: Optional[float] = 0
    notes: Optional[str] = ""
    thickness_in: Optional[float] = 0
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProjectTotalsResponse(BaseModel):
    """Schema for project total calculations"""
    total_entries: int
    total_length_ft: float
    total_weight_lbs: float
    total_weight_tons: float
    total_material_cost: float
    total_labor_hours: float
    total_labor_cost: float
    total_project_cost: float
    by_category: Dict[str, Dict[str, Any]]

class MaterialSearchResult(BaseModel):
    """Schema for material search results"""
    shape_key: str
    category: str
    description: str
    weight_per_ft: float
    unit_price_per_cwt: float
    supplier: str

# Project-related schemas
class TakeoffProjectBase(BaseModel):
    """Base schema for takeoff projects"""
    name: str = Field(..., min_length=1, max_length=255)
    client: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: str = Field("active")

class TakeoffProjectCreate(TakeoffProjectBase):
    """Schema for creating projects"""
    project_id: str = Field(..., min_length=1, max_length=20, description="Manual project ID (e.g., 25-0001)")
    quote_number: str = Field(..., min_length=1, max_length=100)
    estimator: str = Field(..., min_length=1, max_length=255)
    date: Optional[str] = None  # Will be converted to datetime

class TakeoffProjectUpdate(BaseModel):
    """Schema for updating projects"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    client: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None

class TakeoffProjectResponse(BaseModel):
    """Schema for project responses"""
    id: str
    name: str
    client: str  # Maps from client_name in database
    location: Optional[str] = None  # Maps from project_location in database
    description: Optional[str] = None
    status: str = "active"
    quote_number: Optional[str] = None
    estimator: Optional[str] = None
    project_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Project statistics
    total_entries: int = 0
    total_weight_tons: float = 0
    total_value: float = 0
    
    class Config:
        from_attributes = True

# Proposal generation schemas (Phase 5)
class ProposalGenerationRequest(BaseModel):
    """Request for AI-powered proposal generation"""
    project_id: str
    template_type: str = Field("standard", description="Proposal template type")
    include_labor: bool = Field(True, description="Include labor costs in proposal")
    markup_percentage: float = Field(15.0, ge=0, le=100, description="Markup percentage")
    notes: Optional[str] = Field(None, description="Additional project notes")
    include_optimization: bool = Field(False, description="Include material optimization data")
    optimization_id: Optional[int] = Field(None, description="Specific optimization ID to use")
    
class ProposalGenerationResponse(BaseModel):
    """Response from proposal generation"""
    proposal_id: str
    project_id: str
    generated_content: str
    total_amount: float
    created_at: datetime
    
    # Material optimization data
    optimization_included: bool = False
    optimized_material_cost: Optional[float] = None
    material_waste_percentage: Optional[float] = None
    cost_savings: Optional[float] = None
    
    # OpenAI usage
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None

# Bulk save schema for project takeoff entries
class ProjectTakeoffSaveRequest(BaseModel):
    """Request schema for bulk saving project takeoff entries"""
    entries: List[dict] = Field(..., description="List of takeoff entries to save")
    totals: dict = Field(..., description="Calculated project totals")

class ProjectTakeoffSaveResponse(BaseModel):
    """Response schema for bulk save operation"""
    success: bool
    message: str
    entries_saved: int
    project_id: str