from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class TakeoffItem(Base):
    __tablename__ = "takeoff_items"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Material information
    material_shape_key = Column(String, nullable=False)
    description = Column(String)
    
    # Quantities and dimensions
    qty = Column(Float, nullable=False)
    length_ft = Column(Float)  # Standard length in feet
    
    # Plate-specific dimensions (stored as JSON for flexibility)
    plate_dims = Column(JSON)  # {"width_in": 12, "length_ft": 8, "length_in": 6}
    
    # Labor information
    labor_mode = Column(String, default="auto")  # auto or manual
    labor_hours = Column(Float)
    labor_rate = Column(Float, default=120.0)
    labor_description = Column(String)
    
    # Calculated values (cached for performance)
    weight_per_unit = Column(Float)
    total_weight = Column(Float)
    unit_cost = Column(Float)
    material_cost = Column(Float)
    labor_cost = Column(Float)
    total_cost = Column(Float)
    
    # Relationships
    project = relationship("Project", back_populates="takeoff_items")