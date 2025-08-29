"""
Labor Management Schemas - For operations, coatings, and settings
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class OperationType(str, Enum):
    per_ft = "per_ft"
    per_piece = "per_piece"

class CoatingType(str, Enum):
    area = "area"
    weight = "weight" 
    none = "none"

# Labor Operation Schemas
class LaborOperationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rate: Decimal = Field(..., ge=Decimal('0'))
    operation_type: OperationType
    description: Optional[str] = Field(None, max_length=255)
    unit_display: str = Field(..., min_length=1, max_length=50)
    active: bool = True

class LaborOperationCreate(LaborOperationBase):
    pass

class LaborOperationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rate: Optional[Decimal] = Field(None, ge=Decimal('0'))
    operation_type: Optional[OperationType] = None
    description: Optional[str] = Field(None, max_length=255)
    unit_display: Optional[str] = Field(None, min_length=1, max_length=50)
    active: Optional[bool] = None

class LaborOperationResponse(LaborOperationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Coating System Schemas
class CoatingSystemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    coating_type: CoatingType
    rate: Decimal = Field(..., ge=Decimal('0'))
    description: Optional[str] = Field(None, max_length=255)
    unit_display: str = Field(..., min_length=1, max_length=50)
    active: bool = True

class CoatingSystemCreate(CoatingSystemBase):
    pass

class CoatingSystemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    coating_type: Optional[CoatingType] = None
    rate: Optional[Decimal] = Field(None, ge=Decimal('0'))
    description: Optional[str] = Field(None, max_length=255)
    unit_display: Optional[str] = Field(None, min_length=1, max_length=50)
    active: Optional[bool] = None

class CoatingSystemResponse(CoatingSystemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Labor Settings Schemas
class LaborSettingsBase(BaseModel):
    setting_key: str = Field(..., min_length=1, max_length=50)
    setting_value: Decimal = Field(..., ge=Decimal('0'))
    description: Optional[str] = Field(None, max_length=255)
    unit: Optional[str] = Field(None, max_length=20)

class LaborSettingsCreate(LaborSettingsBase):
    pass

class LaborSettingsUpdate(BaseModel):
    setting_value: Decimal = Field(..., ge=Decimal('0'))
    description: Optional[str] = Field(None, max_length=255)
    unit: Optional[str] = Field(None, max_length=20)

class LaborSettingsResponse(LaborSettingsBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True