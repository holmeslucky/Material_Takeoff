"""
Labor Operation Model - Dynamic labor operations with rates
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class OperationType(str, enum.Enum):
    per_ft = "per_ft"
    per_piece = "per_piece"

class LaborOperation(Base):
    __tablename__ = "labor_operations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    rate = Column(Numeric(10, 4), nullable=False)  # Rate in hours or cost
    operation_type = Column(SQLEnum(OperationType), nullable=False)
    description = Column(String(255), nullable=True)
    unit_display = Column(String(50), nullable=False)  # e.g., "per linear foot", "per piece"
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())