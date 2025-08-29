"""
Coating System Model - Dynamic coating systems with rates
"""

from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class CoatingType(str, enum.Enum):
    area = "area"      # Priced per square foot
    weight = "weight"  # Priced per pound
    none = "none"      # No coating

class CoatingSystem(Base):
    __tablename__ = "coating_systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    coating_type = Column(SQLEnum(CoatingType), nullable=False)
    rate = Column(Numeric(10, 4), nullable=False)  # Rate per unit (sqft or lb)
    description = Column(String(255), nullable=True)
    unit_display = Column(String(50), nullable=False)  # e.g., "per square foot", "per pound"
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())