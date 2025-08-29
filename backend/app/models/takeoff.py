"""
Capitol Engineering Company - Takeoff Database Models
SQLAlchemy models for takeoff entries and projects
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class TakeoffProject(Base):
    __tablename__ = "takeoff_projects"
    
    id = Column(String(20), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    client_name = Column(String(255))
    quote_number = Column(String(100))
    estimator = Column(String(255))
    project_location = Column(String(255))
    project_date = Column(DateTime)
    project_number = Column(String(100))
    
    # Project settings
    labor_mode = Column(String(20), default="auto")  # auto or manual
    default_labor_rate = Column(Float, default=120.0)
    project_metadata = Column(JSON, default=dict)  # For storing nesting results and other project metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    entries = relationship("TakeoffEntry", back_populates="project", cascade="all, delete-orphan")

class TakeoffEntry(Base):
    __tablename__ = "takeoff_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(20), ForeignKey("takeoff_projects.id", ondelete="CASCADE"), nullable=False)
    
    # Core takeoff data (11-column structure)
    qty = Column(Integer, nullable=False, default=1)
    shape_key = Column(String(50), nullable=False, index=True)
    description = Column(String(300))
    length_ft = Column(Float, nullable=False, default=0.0)
    width_ft = Column(Float, default=0.0)  # For plates and area calculations
    
    # Material properties
    weight_per_ft = Column(Float, default=0.0)
    unit_price_per_cwt = Column(Float, default=0.0)
    
    # Calculated values
    total_length_ft = Column(Float, default=0.0)
    total_weight_lbs = Column(Float, default=0.0)
    total_weight_tons = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    
    # Labor information
    labor_mode = Column(String(20), default="auto")  # auto, manual, or custom
    labor_hours = Column(Float, default=0.0)
    labor_rate = Column(Float, default=75.0)  # $/hour
    labor_cost = Column(Float, default=0.0)
    labor_type = Column(String(50))  # For custom labor types like "Stairs", "Handrail"
    labor_multiplier = Column(Float, default=1.0)  # Custom multiplier (e.g., 1.25 for stairs)
    
    # Labor operations and coatings
    operations = Column(JSON, default=list)  # Selected labor operations (checkboxes)
    coatings_selected = Column(JSON, default=list)  # Selected coating systems (checkboxes)  
    primary_coating = Column(String(50))  # Primary coating system
    coating_cost = Column(Float, default=0.0)  # Calculated coating cost
    thickness_in = Column(Float, default=0.0)  # For plates - thickness in inches
    
    # Additional metadata
    entry_order = Column(Integer, default=0)  # For maintaining order in UI
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("TakeoffProject", back_populates="entries")
    material = relationship("Material", foreign_keys=[shape_key], primaryjoin="TakeoffEntry.shape_key == Material.shape_key")

class CustomLaborRate(Base):
    __tablename__ = "custom_labor_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # "Stairs", "Handrail", etc.
    description = Column(String(300))
    
    # Labor calculation method
    rate_type = Column(String(20), default="multiplier")  # "multiplier", "fixed_rate", "per_unit"
    multiplier = Column(Float, default=1.0)  # 1.25 for stairs/handrail
    fixed_rate = Column(Float)  # Fixed $/hour if rate_type is "fixed_rate"
    per_unit_rate = Column(Float)  # $/linear_foot if rate_type is "per_unit"
    
    # Application rules
    applies_to_materials = Column(String(500))  # Comma-separated material types or patterns
    applies_to_descriptions = Column(String(500))  # Keywords in descriptions
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())