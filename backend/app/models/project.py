from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, default=1, index=True)  # Multi-tenant support
    name = Column(String, nullable=False)
    customer = Column(String)
    quote_number = Column(String, index=True)
    estimator = Column(String)
    status = Column(String, default="draft")  # draft, active, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    project_data = Column(Text)  # JSON data for additional project info
    
    # Relationships
    takeoff_items = relationship("TakeoffItem", back_populates="project")