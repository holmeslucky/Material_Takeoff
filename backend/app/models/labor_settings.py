"""
Labor Settings Model - Base labor rate, markup, and handling settings
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class LaborSettings(Base):
    __tablename__ = "labor_settings"

    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(50), unique=True, nullable=False, index=True)
    setting_value = Column(Numeric(10, 4), nullable=False)
    description = Column(String(255), nullable=True)
    unit = Column(String(20), nullable=True)  # e.g., "per hour", "percentage"
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())