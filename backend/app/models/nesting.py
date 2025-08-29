"""
Capitol Engineering Company - Nesting & Material Optimization Models
Database models for storing nesting optimization results and material data
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class StandardMaterialSize(Base):
    """Standard material sizes available from suppliers"""
    __tablename__ = "standard_material_sizes"
    
    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String(50), nullable=False, index=True)  # PLATE, BEAM, ANGLE, etc.
    shape_category = Column(String(50), index=True)  # W-shapes, L-shapes, Plates, etc.
    
    # Dimensions
    length_ft = Column(Float)
    width_in = Column(Float)  # For plates
    height_in = Column(Float)  # For beams/channels
    thickness_in = Column(Float)  # For plates, web thickness for beams
    
    # Pricing
    cost_per_unit = Column(Numeric(10, 2))  # Cost per piece
    cost_per_foot = Column(Numeric(10, 2))  # Cost per foot (for linear materials)
    cost_per_sqft = Column(Numeric(10, 2))  # Cost per square foot (for plates)
    
    # Supplier information
    supplier_name = Column(String(100), index=True)
    supplier_code = Column(String(50))
    availability = Column(String(20), default="standard")  # standard, special_order, unavailable
    lead_time_days = Column(Integer, default=0)
    
    # Usage tracking
    commonly_used = Column(Boolean, default=False, index=True)
    last_used_date = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NestingOptimization(Base):
    """Stores nesting optimization results for projects"""
    __tablename__ = "nesting_optimizations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), ForeignKey("takeoff_projects.id"), nullable=False, index=True)
    optimization_name = Column(String(200))  # User-friendly name for the optimization
    
    # Optimization parameters
    optimization_level = Column(String(20), default="standard")  # basic, standard, advanced
    include_waste_costs = Column(Boolean, default=True)
    algorithm_version = Column(String(20), default="1.0")
    
    # Results summary
    total_material_cost = Column(Numeric(12, 2))
    total_waste_cost = Column(Numeric(12, 2))
    total_waste_percentage = Column(Float)
    cost_savings = Column(Numeric(12, 2))  # Savings vs non-optimized
    efficiency_rating = Column(Float)  # 0-100 score
    
    # Optimization metadata
    optimization_summary = Column(Text)
    recommendations = Column(JSON)  # List of recommendations
    algorithm_details = Column(JSON)  # Technical details about algorithm used
    
    # Status
    status = Column(String(20), default="completed")  # pending, running, completed, failed
    is_active = Column(Boolean, default=True)  # Current active optimization for project
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("TakeoffProject")
    material_purchases = relationship("MaterialPurchaseRecommendation", back_populates="optimization")

class MaterialPurchaseRecommendation(Base):
    """Individual material purchase recommendations from nesting optimization"""
    __tablename__ = "material_purchase_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_id = Column(Integer, ForeignKey("nesting_optimizations.id"), nullable=False, index=True)
    
    # Material identification
    shape_key = Column(String(50), nullable=False, index=True)
    size_description = Column(String(200))  # Human-readable size description
    material_type = Column(String(50), index=True)
    
    # Standard size used
    standard_size_id = Column(Integer, ForeignKey("standard_material_sizes.id"))
    standard_length_ft = Column(Float)
    standard_width_in = Column(Float)
    standard_thickness_in = Column(Float)
    
    # Purchase details
    pieces_needed = Column(Integer, nullable=False)
    total_cost = Column(Numeric(10, 2))
    unit_cost = Column(Numeric(10, 2))
    
    # Waste analysis
    waste_percentage = Column(Float)
    waste_cost = Column(Numeric(10, 2))
    utilization_percentage = Column(Float)  # 100 - waste_percentage
    
    # Cutting details
    cuts_data = Column(JSON)  # List of cuts that will be made from this material
    cuts_count = Column(Integer)
    
    # Supplier information
    preferred_supplier = Column(String(100))
    supplier_quote = Column(Numeric(10, 2))
    delivery_date = Column(DateTime(timezone=True))
    
    # Priority and status
    priority = Column(String(20), default="normal")  # critical, high, normal, low
    purchase_status = Column(String(20), default="recommended")  # recommended, ordered, delivered
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    optimization = relationship("NestingOptimization", back_populates="material_purchases")
    standard_size = relationship("StandardMaterialSize")

class MaterialWasteAnalysis(Base):
    """Detailed waste analysis for materials and cutting patterns"""
    __tablename__ = "material_waste_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), ForeignKey("takeoff_projects.id"), nullable=False, index=True)
    optimization_id = Column(Integer, ForeignKey("nesting_optimizations.id"), index=True)
    
    # Material details
    shape_key = Column(String(50), nullable=False, index=True)
    material_type = Column(String(50), index=True)
    
    # Waste calculations
    material_required_area = Column(Float)  # Total area needed (for plates)
    material_required_length = Column(Float)  # Total length needed (for linear materials)
    material_purchased_area = Column(Float)  # Total area purchased
    material_purchased_length = Column(Float)  # Total length purchased
    
    waste_area = Column(Float)
    waste_length = Column(Float)
    waste_percentage = Column(Float)
    waste_cost = Column(Numeric(10, 2))
    
    # Drop analysis
    drops_data = Column(JSON)  # List of drop pieces with dimensions
    usable_drops_count = Column(Integer, default=0)
    usable_drops_value = Column(Numeric(10, 2), default=0)
    scrap_weight_lbs = Column(Float)
    scrap_value = Column(Numeric(10, 2))
    
    # Optimization opportunities
    alternative_sizes_considered = Column(JSON)
    optimization_suggestions = Column(JSON)
    potential_savings = Column(Numeric(10, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NestingPattern(Base):
    """Stores actual nesting patterns and cutting layouts"""
    __tablename__ = "nesting_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_id = Column(Integer, ForeignKey("nesting_optimizations.id"), nullable=False, index=True)
    purchase_recommendation_id = Column(Integer, ForeignKey("material_purchase_recommendations.id"), index=True)
    
    # Pattern identification
    pattern_name = Column(String(100))
    material_piece_number = Column(Integer)  # Which piece of material this pattern is for
    
    # Material dimensions
    material_length_ft = Column(Float)
    material_width_in = Column(Float)
    material_thickness_in = Column(Float)
    
    # Cutting pattern data
    cutting_pattern = Column(JSON)  # Detailed layout with coordinates
    cuts_list = Column(JSON)  # List of cuts with dimensions and positions
    
    # Pattern efficiency
    utilization_percentage = Column(Float)
    waste_pieces = Column(JSON)  # Waste pieces with dimensions
    
    # Production information
    cutting_time_minutes = Column(Float)
    cutting_complexity = Column(String(20))  # simple, moderate, complex
    special_requirements = Column(Text)  # Notes for production
    
    # Status
    approved = Column(Boolean, default=False)
    production_ready = Column(Boolean, default=False)
    cutting_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    optimization = relationship("NestingOptimization")
    purchase_recommendation = relationship("MaterialPurchaseRecommendation")