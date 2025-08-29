from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'Main Takeoff', 'Ductwork Takeoff', 'Pipe Takeoff'
    description = Column(Text, nullable=True)
    items = Column(JSON, nullable=False, default=[])  # JSON array of template items
    calculator_settings = Column(JSON, nullable=True, default={})  # Calculator configurations
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    modified_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())