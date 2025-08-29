from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.session import SessionLocal
from app.models.material import Material

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/search")
def search_materials(
    q: str = Query("", description="Search query for material name or type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Search materials - matches desktop functionality
    Fast search with < 150ms response time target
    """
    query = db.query(Material)
    
    # Search in shape_key and material_type (matches desktop logic)
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Material.shape_key.ilike(like_pattern),
                Material.material_type.ilike(like_pattern)
            )
        )
    
    # Category filter
    if category:
        query = query.filter(Material.category == category)
    
    # Order by commonly used first, then alphabetically (matches desktop)
    query = query.order_by(
        Material.commonly_used.desc(), 
        Material.shape_key.asc()
    ).limit(limit)
    
    materials = query.all()
    
    # Return format matching desktop expectations
    return [
        {
            "shape_key": material.shape_key,
            "material_type": material.material_type,
            "grade": material.grade,
            "weight_per_ft": material.weight_per_ft,
            "price_per_lb": material.price_per_lb,
            "price_per_ft": material.price_per_ft,
            "category": material.category,
            "commonly_used": material.commonly_used
        }
        for material in materials
    ]

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get all available material categories"""
    categories = db.query(Material.category).distinct().all()
    return [category[0] for category in categories if category[0]]

@router.get("/{shape_key}")
def get_material_by_shape_key(shape_key: str, db: Session = Depends(get_db)):
    """Get specific material by shape key"""
    material = db.query(Material).filter(Material.shape_key == shape_key).first()
    if not material:
        raise HTTPException(404, f"Material {shape_key} not found")
    
    return {
        "shape_key": material.shape_key,
        "material_type": material.material_type,
        "grade": material.grade,
        "weight_per_ft": material.weight_per_ft,
        "price_per_lb": material.price_per_lb,
        "price_per_ft": material.price_per_ft,
        "category": material.category,
        "commonly_used": material.commonly_used
    }

@router.post("/import")
def import_materials():
    """Import materials from Excel (placeholder for admin functionality)"""
    # TODO: Implement Excel import matching desktop functionality
    return {"message": "Material import functionality will be implemented in Phase 3"}

@router.get("/")
def list_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all materials with pagination"""
    query = db.query(Material)
    
    if category:
        query = query.filter(Material.category == category)
    
    materials = query.offset(skip).limit(limit).all()
    total_count = query.count()
    
    return {
        "materials": [
            {
                "shape_key": material.shape_key,
                "material_type": material.material_type,
                "category": material.category,
                "weight_per_ft": material.weight_per_ft,
                "price_per_ft": material.price_per_ft
            }
            for material in materials
        ],
        "total_count": total_count,
        "skip": skip,
        "limit": limit
    }