from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    shape_key = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(300))
    category = Column(String(50), index=True)  # Wide Flange, Plate, Angle, etc.
    material_type = Column(String(50))  # Steel, Aluminum, etc.
    grade = Column(String(20))  # A36, A992, etc.
    
    # Physical properties
    weight_per_ft = Column(Float)  # Legacy structural steel weight per foot
    depth_inches = Column(Float)
    width_inches = Column(Float) 
    thickness_inches = Column(Float)
    
    # Pricing (backwards compatible)
    unit_price_per_cwt = Column(Float)  # Legacy price per 100 lbs (CWT)
    supplier = Column(String(100))
    
    # Usage tracking
    commonly_used = Column(Boolean, default=False, index=True)
    last_used_date = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Blake's comprehensive material fields (all nullable for backwards compatibility)
    subcategory = Column(String(50), index=True)  # Fitting, Pipe, Valve, Component, Flange
    specs_standard = Column(String(100), index=True)  # ASTM 316L, A106B, API 5L, etc.
    base_price_usd = Column(Float)  # Blake's comprehensive pricing
    size_dimensions = Column(String(200))  # Size/dimensions from Blake's data
    schedule_class = Column(String(50))  # Schedule/Class for pipes and fittings
    finish_coating = Column(String(100))  # Mill, Galvanized, Painted, etc.
    weight_per_uom = Column(Float)  # Weight per unit of measure (Blake's data)
    unit_of_measure = Column(String(20), default="ft")  # each, ft, lb, sq ft, etc.
    source_system = Column(String(20), default="legacy", index=True)  # Track data origin
    sku_part_number = Column(String(100))  # SKU/Part number
    notes = Column(Text)  # Additional notes
    price_confidence = Column(String(20), default="high")  # high, medium, low
    last_price_update = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property 
    def effective_price(self):
        """Get the most appropriate price for this material"""
        # Use Blake's pricing if available, otherwise fall back to CWT pricing
        if self.base_price_usd:
            return self.base_price_usd
        elif self.unit_price_per_cwt and self.weight_per_ft:
            # Convert CWT pricing to total price (assuming per foot)
            return (self.unit_price_per_cwt / 100.0) * self.weight_per_ft
        return None
    
    @property
    def effective_weight(self):
        """Get the most appropriate weight for this material"""
        # Use Blake's weight data if available, otherwise structural weight
        return self.weight_per_uom if self.weight_per_uom else self.weight_per_ft
    
    @property
    def full_designation(self):
        """Get comprehensive material designation"""
        if self.source_system == "blake" and self.size_dimensions:
            return f"{self.shape_key} - {self.size_dimensions}"
        return self.shape_key
    
    @property
    def category_display(self):
        """Get display-friendly category"""
        if self.subcategory:
            return f"{self.category}/{self.subcategory}"
        return self.category
    
    def __repr__(self):
        price = self.effective_price
        price_str = f"${price:.2f}" if price else "No price"
        return f"<Material({self.shape_key}, {self.category_display}, {price_str})>"