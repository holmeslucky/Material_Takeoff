"""
Capitol Engineering Company - Materials API Endpoints
Material database management and search functionality
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.material import Material
from app.models.user import User
from app.core.security import verify_password, create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

# Authentication endpoint added to materials router as emergency fix
@router.post("/auth-login")
async def emergency_auth_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Emergency login endpoint in materials router"""
    try:
        email = request.email
        password = request.password 
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
            
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account inactive")
            
        token = create_access_token(str(user.id))
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/")
async def search_materials(
    q: str = Query(None, description="Search term for materials"),
    category: str = Query(None, description="Filter by category"),
    subcategory: str = Query(None, description="Filter by subcategory (Fitting, Pipe, Valve, etc.)"),
    specs: str = Query(None, description="Filter by specifications/standard (ASTM 316L, etc.)"),
    price_min: float = Query(None, description="Minimum price filter"),
    price_max: float = Query(None, description="Maximum price filter"),
    source: str = Query(None, description="Filter by source (legacy, blake)"),
    limit: int = Query(100, description="Maximum results"),
    skip: int = Query(0, description="Number of results to skip for pagination"),
    db: Session = Depends(get_db)
):
    """
    Enhanced search materials database
    Supports Blake's comprehensive material database with advanced filtering
    """
    
    query = db.query(Material)
    
    # Search filter - enhanced for Blake's data
    if q:
        search_filter = (
            Material.shape_key.ilike(f"%{q}%") |
            Material.description.ilike(f"%{q}%") |
            Material.specs_standard.ilike(f"%{q}%") |
            Material.size_dimensions.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    # Category filter
    if category and category != 'all':
        query = query.filter(Material.category == category)
    
    # Subcategory filter (Blake's data)
    if subcategory and subcategory != 'all':
        query = query.filter(Material.subcategory == subcategory)
    
    # Specifications filter
    if specs:
        query = query.filter(Material.specs_standard.ilike(f"%{specs}%"))
    
    # Price range filters
    if price_min is not None:
        query = query.filter(
            (Material.base_price_usd >= price_min) |
            (Material.base_price_usd.is_(None) & (Material.unit_price_per_cwt * Material.weight_per_ft / 100 >= price_min))
        )
    if price_max is not None:
        query = query.filter(
            (Material.base_price_usd <= price_max) |
            (Material.base_price_usd.is_(None) & (Material.unit_price_per_cwt * Material.weight_per_ft / 100 <= price_max))
        )
    
    # Source filter
    if source and source != 'all':
        query = query.filter(Material.source_system == source)
    
    # Smart ordering - prioritize commonly used, then by price
    query = query.order_by(
        Material.commonly_used.desc(),
        Material.category,
        Material.subcategory,
        Material.shape_key
    )
    
    # Apply pagination and limit
    materials = query.offset(skip).limit(limit).all()
    
    # Return enhanced material data - comprehensive Blake's integration
    return [
        {
            "id": m.id,
            "shape_key": m.shape_key,
            "category": m.category,
            "subcategory": m.subcategory,
            "description": m.description or m.full_designation,
            "specs_standard": m.specs_standard,
            "size_dimensions": m.size_dimensions,
            "finish_coating": m.finish_coating,
            
            # Pricing - use effective price that handles both systems
            "price": m.effective_price,
            "unit_price_per_cwt": float(m.unit_price_per_cwt) if m.unit_price_per_cwt else None,
            "base_price_usd": float(m.base_price_usd) if m.base_price_usd else None,
            "price_confidence": m.price_confidence,
            
            # Weight
            "weight": m.effective_weight,
            "weight_per_ft": float(m.weight_per_ft) if m.weight_per_ft else None,
            "weight_per_uom": float(m.weight_per_uom) if m.weight_per_uom else None,
            "unit_of_measure": m.unit_of_measure,
            
            # Metadata
            "supplier": m.supplier or "Unknown",
            "source_system": m.source_system,
            "commonly_used": m.commonly_used,
            "last_updated": m.updated_at
        }
        for m in materials
    ]

@router.get("/enhanced")
async def search_materials_enhanced(
    q: str = Query(None, description="Search term for materials"),
    category: str = Query(None, description="Filter by category"),
    subcategory: str = Query(None, description="Filter by subcategory"),
    limit: int = Query(100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    TEST Enhanced search materials database - comprehensive Blake's integration
    """
    
    query = db.query(Material)
    
    # Basic filters
    if q:
        query = query.filter(Material.shape_key.ilike(f"%{q}%"))
    if category and category != 'all':
        query = query.filter(Material.category == category)
    if subcategory and subcategory != 'all':
        query = query.filter(Material.subcategory == subcategory)
    
    materials = query.limit(limit).all()
    
    # Return enhanced format
    return [
        {
            "id": m.id,
            "shape_key": m.shape_key,
            "category": m.category,
            "subcategory": m.subcategory,
            "description": m.description or m.full_designation,
            "specs_standard": m.specs_standard,
            "size_dimensions": m.size_dimensions,
            "finish_coating": m.finish_coating,
            "price": m.effective_price,
            "unit_price_per_cwt": float(m.unit_price_per_cwt) if m.unit_price_per_cwt else None,
            "base_price_usd": float(m.base_price_usd) if m.base_price_usd else None,
            "price_confidence": m.price_confidence,
            "weight": m.effective_weight,
            "weight_per_ft": float(m.weight_per_ft) if m.weight_per_ft else None,
            "weight_per_uom": float(m.weight_per_uom) if m.weight_per_uom else None,
            "unit_of_measure": m.unit_of_measure,
            "supplier": m.supplier or "Unknown",
            "source_system": m.source_system,
            "commonly_used": m.commonly_used,
            "last_updated": m.updated_at
        }
        for m in materials
    ]

@router.get("/categories")
async def get_material_categories(db: Session = Depends(get_db)):
    """Get all available material categories"""
    
    categories = db.query(Material.category).distinct().all()
    return [category[0] for category in categories if category[0]]

@router.get("/subcategories")
async def get_material_subcategories(
    category: str = Query(None, description="Filter subcategories by category"),
    db: Session = Depends(get_db)
):
    """Get all available material subcategories"""
    
    query = db.query(Material.subcategory).filter(Material.subcategory.isnot(None)).distinct()
    
    if category:
        query = query.filter(Material.category == category)
    
    subcategories = query.all()
    return [subcat[0] for subcat in subcategories if subcat[0]]

@router.get("/specifications")
async def get_material_specifications(db: Session = Depends(get_db)):
    """Get all available material specifications/standards"""
    
    specs = db.query(Material.specs_standard).filter(
        Material.specs_standard.isnot(None)
    ).distinct().limit(50).all()
    
    return [spec[0] for spec in specs if spec[0]]

@router.get("/fittings")
async def search_fittings(
    q: str = Query(None, description="Search fittings"),
    specs: str = Query(None, description="Filter by ASTM standard"),
    size: str = Query(None, description="Filter by size"),
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Search fittings specifically"""
    
    query = db.query(Material).filter(Material.subcategory == 'Fitting')
    
    if q:
        query = query.filter(Material.shape_key.ilike(f"%{q}%"))
    
    if specs:
        query = query.filter(Material.specs_standard.ilike(f"%{specs}%"))
    
    if size:
        query = query.filter(Material.size_dimensions.ilike(f"%{size}%"))
    
    fittings = query.order_by(Material.base_price_usd).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "shape_key": m.shape_key,
            "description": m.full_designation,
            "specs_standard": m.specs_standard,
            "size_dimensions": m.size_dimensions,
            "price": m.effective_price,
            "supplier": m.supplier
        }
        for m in fittings
    ]

@router.get("/pipes")
async def search_pipes(
    q: str = Query(None, description="Search pipes"),
    specs: str = Query(None, description="Filter by ASTM standard"), 
    schedule: str = Query(None, description="Filter by schedule"),
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """Search pipes specifically"""
    
    query = db.query(Material).filter(Material.subcategory == 'Pipe')
    
    if q:
        query = query.filter(Material.shape_key.ilike(f"%{q}%"))
    
    if specs:
        query = query.filter(Material.specs_standard.ilike(f"%{specs}%"))
    
    if schedule:
        query = query.filter(Material.schedule_class.ilike(f"%{schedule}%"))
    
    pipes = query.order_by(Material.base_price_usd).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "shape_key": m.shape_key,
            "description": m.full_designation,
            "specs_standard": m.specs_standard,
            "schedule_class": m.schedule_class,
            "size_dimensions": m.size_dimensions,
            "price": m.effective_price,
            "weight": m.effective_weight,
            "supplier": m.supplier
        }
        for m in pipes
    ]

@router.get("/by-shape/{shape_key}")
async def get_material_by_shape(shape_key: str, db: Session = Depends(get_db)):
    """Get material by shape key (e.g., W12X26, PL1/2X12)"""
    
    material = db.query(Material).filter(
        Material.shape_key.ilike(shape_key)
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail=f"Material {shape_key} not found")
    
    return {
        "id": material.id,
        "shape_key": material.shape_key,
        "category": material.category,
        "description": material.description,
        "weight_per_ft": float(material.weight_per_ft) if material.weight_per_ft else None,
        "unit_price_per_cwt": float(material.unit_price_per_cwt) if material.unit_price_per_cwt else None,
        "supplier": material.supplier or "Unknown",
        "dimensions": getattr(material, 'dimensions', ''),
        "last_updated": getattr(material, 'last_updated', None)
    }

@router.get("/{material_id}")
async def get_material(material_id: int, db: Session = Depends(get_db)):
    """Get specific material by ID"""
    
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    return {
        "id": material.id,
        "shape_key": material.shape_key,
        "category": material.category,
        "description": material.description,
        "weight_per_ft": float(material.weight_per_ft) if material.weight_per_ft else None,
        "unit_price_per_cwt": float(material.unit_price_per_cwt) if material.unit_price_per_cwt else None,
        "supplier": material.supplier or "Unknown",
        "dimensions": getattr(material, 'dimensions', ''),
        "last_updated": getattr(material, 'last_updated', None)
    }