"""
Capitol Engineering Company - Takeoff API Endpoints
Real-time takeoff calculations and entry management
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.takeoff import TakeoffEntry, TakeoffProject
from app.models.material import Material
from app.services.takeoff_service import TakeoffCalculationService
from app.schemas.takeoff import (
    TakeoffEntryCreate, TakeoffEntryUpdate, TakeoffEntryResponse,
    TakeoffCalculationRequest, TakeoffCalculationResponse,
    ProjectTotalsResponse
)

router = APIRouter()
takeoff_service = TakeoffCalculationService()

@router.get("/projects/{project_id}/entries")
async def get_project_entries(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Load all takeoff entries for a specific project
    Returns entries in the format expected by TakeoffGrid frontend
    """
    
    try:
        # Verify project exists
        project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        # Get all entries for this project
        db_entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
        
        # Convert to frontend format with better error handling
        entries = []
        for entry in db_entries:
            try:
                entry_data = {
                    "id": str(entry.id) if entry.id else str(hash(str(entry))),
                    "qty": int(entry.qty) if entry.qty else 1,
                    "shape_key": str(entry.shape_key) if entry.shape_key else "",
                    "description": str(entry.description) if entry.description else "",
                    "length_ft": float(entry.length_ft) if entry.length_ft else 0.0,
                    "length_in": float(getattr(entry, 'length_in', 0) or 0),
                    "width_in": float((entry.width_ft * 12) if entry.width_ft else 0),  # Convert feet to inches
                    "thickness_in": float(getattr(entry, 'thickness_in', 0) or 0),
                    "weight_per_ft": float(entry.weight_per_ft) if entry.weight_per_ft else 0.0,
                    "total_length_ft": float(entry.total_length_ft) if entry.total_length_ft else 0.0,
                    "total_weight_lbs": float(entry.total_weight_lbs) if entry.total_weight_lbs else 0.0,
                    "total_weight_tons": float(entry.total_weight_tons) if entry.total_weight_tons else 0.0,
                    "unit_price_per_cwt": float(entry.unit_price_per_cwt) if entry.unit_price_per_cwt else 0.0,
                    "total_price": float(entry.total_price) if entry.total_price else 0.0,
                    "labor_hours": float(entry.labor_hours) if entry.labor_hours else 0.0,
                    "labor_cost": float(entry.labor_cost) if entry.labor_cost else 0.0,
                    "operations": list(getattr(entry, 'operations', []) or []),
                    "coatings_selected": list(getattr(entry, 'coatings_selected', []) or []),
                    "primary_coating": str(getattr(entry, 'primary_coating', '') or ''),
                    "coating_cost": float(getattr(entry, 'coating_cost', 0) or 0),
                    "notes": str(entry.notes) if entry.notes else ''
                }
                entries.append(entry_data)
            except Exception as e:
                print(f"Warning: Could not convert entry {entry.id}: {str(e)}")
                # Skip problematic entries instead of failing completely
                continue
        
        return entries
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error loading entries for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load takeoff entries: {str(e)}"
        )

@router.post("/calculate", response_model=TakeoffCalculationResponse)
async def calculate_takeoff_entry(
    request: TakeoffCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate takeoff entry values in real-time
    Matches desktop application 11-column calculation logic
    """
    
    # Get material data from database if shape_key provided
    material_data = None
    material_confirmed = False
    if request.shape_key:
        try:
            material_data = db.query(Material).filter(
                Material.shape_key == request.shape_key.upper()
            ).first()
            material_confirmed = bool(material_data)
        except:
            # Database not available, use fallback data
            material_data = None
            material_confirmed = False
    
    # Convert inches to feet for backend compatibility
    width_ft = (request.width_in or 0.0) / 12.0 if request.width_in else 0.0
    # Combine length_ft and length_in into total length in feet
    total_length_ft = request.length_ft + ((request.length_in or 0.0) / 12.0)
    
    # Calculate entry values
    try:
        calculation = takeoff_service.calculate_entry(
            qty=request.qty,
            shape_key=request.shape_key,
            length_ft=total_length_ft,
            width_ft=width_ft,
            material_data=material_data,
            unit_price_per_cwt=request.unit_price_per_cwt
        )
    except ValueError as e:
        # Handle specific calculation errors (like plates requiring width)
        raise HTTPException(status_code=400, detail=str(e))
    
    # Calculate labor if requested
    if request.calculate_labor:
        labor_calc = takeoff_service.calculate_labor_hours(
            material_key=request.shape_key,
            qty=request.qty,
            length_ft=request.length_ft,
            mode=request.labor_mode or 'auto',
            operations=[op.value if hasattr(op, "value") else op for op in (request.operations or [])]
        )
        calculation.update(labor_calc)
    
    # Calculate coatings
    coatings_calc = takeoff_service.calculate_coatings(
        material_key=request.shape_key,
        qty=request.qty,
        length_ft=total_length_ft,
        width_ft=width_ft,
        total_weight_lbs=calculation.get("total_weight_lbs"),
        coatings_selected=[c.value if hasattr(c, "value") else c for c in (request.coatings_selected or [])],
        primary=request.primary_coating,
    )
    calculation.update(coatings_calc)
    
    # Add material confirmation and enforce locked description
    calculation["material_confirmed"] = material_confirmed
    if material_confirmed and material_data:
        calculation["description"] = material_data.description
        calculation["category"] = getattr(material_data, "category", calculation.get("category", "Other"))
    
    return TakeoffCalculationResponse(**calculation)

@router.get("/materials/search")
async def search_materials(
    q: str = Query(..., description="Search term for materials"),
    category: str = Query(None, description="Filter by category"),
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Smart search for materials with pattern-based filtering
    - W6 shows all W6x variants (W6X9, W6X12, W6X15, etc.)
    - PL shows common plate thicknesses (PL1/4, PL3/16, PL1/2, PL.500, PL.250, etc.)
    """
    
    query = db.query(Material)
    q_upper = q.upper().strip()
    
    # Clean, simple search - prioritize exact and prefix matches
    search_filter = (
        Material.shape_key.ilike(f"{q_upper}%") |
        Material.description.ilike(f"%{q_upper}%")
    )
    
    query = query.filter(search_filter)
    
    # Category filter
    if category:
        query = query.filter(Material.category == category)
    
    # Order by relevance: exact matches first, then starts with, then contains
    materials = query.limit(limit).all()
    
    # Sort results for better relevance
    sorted_materials = sorted(materials, key=lambda m: (
        0 if m.shape_key.upper() == q_upper else
        1 if m.shape_key.upper().startswith(q_upper) else
        2,
        m.shape_key
    ))
    
    return [
        {
            "shape_key": m.shape_key,
            "category": m.category,
            "description": m.description,
            "weight_per_ft": float(m.weight_per_ft),
            "unit_price_per_cwt": float(m.unit_price_per_cwt),
            "supplier": m.supplier
        }
        for m in sorted_materials
    ]

@router.get("/projects/{project_id}/entries", response_model=List[TakeoffEntryResponse])
async def get_project_takeoff_entries(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get all takeoff entries for a project"""
    
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == project_id
    ).order_by(TakeoffEntry.created_at).all()
    
    return entries

@router.post("/projects/{project_id}/entries", response_model=TakeoffEntryResponse)
async def create_takeoff_entry(
    project_id: str,
    entry_data: TakeoffEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new takeoff entry with calculations"""
    
    # Get material data for calculations
    material_data = None
    if entry_data.shape_key:
        material_data = db.query(Material).filter(
            Material.shape_key == entry_data.shape_key.upper()
        ).first()
    
    # Calculate entry values
    calculation = takeoff_service.calculate_entry(
        qty=entry_data.qty,
        shape_key=entry_data.shape_key,
        length_ft=entry_data.length_ft,
        width_ft=entry_data.width_ft or 0.0,
        material_data=material_data
    )
    
    # Calculate labor
    labor_calc = takeoff_service.calculate_labor_hours(
        material_key=entry_data.shape_key,
        qty=entry_data.qty,
        length_ft=entry_data.length_ft,
        mode=entry_data.labor_mode or 'auto'
    )
    
    # Create database entry
    db_entry = TakeoffEntry(
        project_id=project_id,
        qty=entry_data.qty,
        shape_key=entry_data.shape_key.upper(),
        description=calculation['description'],
        length_ft=entry_data.length_ft,
        width_ft=entry_data.width_ft or 0.0,
        thickness_in=getattr(entry_data, 'thickness_in', 0.0),
        weight_per_ft=calculation['weight_per_ft'],
        total_length_ft=calculation['total_length_ft'],
        total_weight_lbs=calculation['total_weight_lbs'],
        total_weight_tons=calculation['total_weight_tons'],
        unit_price_per_cwt=calculation['unit_price_per_cwt'],
        total_price=calculation['total_price'],
        labor_hours=labor_calc['labor_hours'],
        labor_rate=labor_calc['labor_rate'],
        labor_cost=labor_calc['labor_cost'],
        labor_mode=labor_calc['mode'],
        operations=entry_data.operations or [],
        coatings_selected=entry_data.coatings_selected or [],
        primary_coating=entry_data.primary_coating or '',
        coating_cost=getattr(entry_data, 'coating_cost', 0.0),
        notes=getattr(entry_data, 'notes', '')
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@router.put("/entries/{entry_id}", response_model=TakeoffEntryResponse)
async def update_takeoff_entry(
    entry_id: int,
    entry_update: TakeoffEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update takeoff entry with recalculation"""
    
    db_entry = db.query(TakeoffEntry).filter(TakeoffEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Takeoff entry not found")
    
    # Update fields
    for field, value in entry_update.dict(exclude_unset=True).items():
        setattr(db_entry, field, value)
    
    # Recalculate if key fields changed
    if any(field in entry_update.dict(exclude_unset=True) for field in 
           ['qty', 'shape_key', 'length_ft', 'width_ft']):
        
        # Get material data
        material_data = db.query(Material).filter(
            Material.shape_key == db_entry.shape_key
        ).first()
        
        # Recalculate
        calculation = takeoff_service.calculate_entry(
            qty=db_entry.qty,
            shape_key=db_entry.shape_key,
            length_ft=db_entry.length_ft,
            width_ft=db_entry.width_ft,
            material_data=material_data
        )
        
        # Update calculated fields
        db_entry.total_length_ft = calculation['total_length_ft']
        db_entry.total_weight_lbs = calculation['total_weight_lbs']
        db_entry.total_weight_tons = calculation['total_weight_tons']
        db_entry.total_price = calculation['total_price']
        
        # Recalculate labor
        labor_calc = takeoff_service.calculate_labor_hours(
            material_key=db_entry.shape_key,
            qty=db_entry.qty,
            length_ft=db_entry.length_ft,
            mode=db_entry.labor_mode
        )
        
        db_entry.labor_hours = labor_calc['labor_hours']
        db_entry.labor_cost = labor_calc['labor_cost']
    
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@router.delete("/entries/{entry_id}")
async def delete_takeoff_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Delete takeoff entry"""
    
    db_entry = db.query(TakeoffEntry).filter(TakeoffEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Takeoff entry not found")
    
    db.delete(db_entry)
    db.commit()
    
    return {"message": "Takeoff entry deleted successfully"}

@router.delete("/projects/{project_id}/entries")
async def delete_all_project_entries(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Delete all takeoff entries for a project (bulk delete for safe replace pattern)"""
    
    # No need to verify project exists - we just want to delete entries
    # This is safer and more flexible for the bulk replace pattern
    
    # Get count of entries to delete
    entries_count = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).count()
    
    if entries_count == 0:
        # Return success even if no entries to delete
        return {
            "message": f"No entries found for project {project_id} - nothing to delete",
            "entries_deleted": 0,
            "project_id": project_id
        }
    
    # Delete all entries for this project
    deleted_count = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).delete()
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} entries for project {project_id}",
        "entries_deleted": deleted_count,
        "project_id": project_id
    }

@router.get("/projects/{project_id}/totals", response_model=ProjectTotalsResponse)
async def get_project_totals(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Calculate project totals from all takeoff entries"""
    
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == project_id
    ).all()
    
    # Convert to dict format for service
    entry_dicts = []
    for entry in entries:
        entry_dict = {
            'total_length_ft': entry.total_length_ft,
            'total_weight_lbs': entry.total_weight_lbs,
            'total_weight_tons': entry.total_weight_tons,
            'total_price': entry.total_price,
            'labor_hours': entry.labor_hours or 0,
            'labor_cost': entry.labor_cost or 0,
            'category': entry.material.category if entry.material else 'Other'
        }
        entry_dicts.append(entry_dict)
    
    # Calculate totals using service
    totals = takeoff_service.calculate_project_totals(entry_dicts)
    
    return ProjectTotalsResponse(**totals)

@router.get("/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint to check database connection and Material table"""
    try:
        from sqlalchemy import text
        
        # Test basic database connection
        result = db.execute(text("SELECT 1")).scalar()
        
        # Check if Material table exists
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [table[0] for table in tables]
        
        # If Material table exists, get sample data
        material_sample = None
        material_count = 0
        if "materials" in table_names:
            material_count = db.execute(text("SELECT COUNT(*) FROM materials")).scalar()
            if material_count > 0:
                material_sample = db.execute(text("SELECT shape_key, description FROM materials LIMIT 3")).fetchall()
        
        return {
            "database_connected": bool(result),
            "tables": table_names,
            "materials_table_exists": "materials" in table_names,
            "material_count": material_count,
            "sample_materials": [{"shape_key": row[0], "description": row[1]} for row in (material_sample or [])]
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@router.get("/categories")
async def get_material_categories(db: Session = Depends(get_db)):
    """Get all available material categories"""
    
    categories = db.query(Material.category).distinct().all()
    return [category[0] for category in categories]

@router.get("/descriptions/search")
async def search_descriptions(
    q: str = Query(..., description="Search term for material descriptions"),
    limit: int = Query(20, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search material descriptions independently of shape_key
    Provides autocomplete functionality for description field
    """
    
    query = db.query(Material.description).distinct()
    
    # Search in description text
    search_filter = Material.description.ilike(f"%{q}%")
    query = query.filter(search_filter)
    
    # Order by relevance (starts with query first, then contains)
    descriptions = query.limit(limit).all()
    
    # Extract description strings and sort by relevance
    desc_list = [desc[0] for desc in descriptions if desc[0]]
    
    # Sort by relevance: exact match first, starts with next, contains last
    def sort_key(desc):
        desc_lower = desc.lower()
        q_lower = q.lower()
        if desc_lower == q_lower:
            return (0, desc)
        elif desc_lower.startswith(q_lower):
            return (1, desc)
        else:
            return (2, desc)
    
    sorted_descriptions = sorted(desc_list, key=sort_key)
    
    return sorted_descriptions[:limit]

@router.post("/projects/{project_id}/duplicate-entry/{entry_id}")
async def duplicate_takeoff_entry(
    project_id: str,
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Duplicate an existing takeoff entry"""
    
    original_entry = db.query(TakeoffEntry).filter(TakeoffEntry.id == entry_id).first()
    if not original_entry:
        raise HTTPException(status_code=404, detail="Takeoff entry not found")
    
    # Create duplicate with same values
    duplicate_entry = TakeoffEntry(
        project_id=project_id,
        qty=original_entry.qty,
        shape_key=original_entry.shape_key,
        description=original_entry.description,
        length_ft=original_entry.length_ft,
        width_ft=original_entry.width_ft,
        weight_per_ft=original_entry.weight_per_ft,
        total_length_ft=original_entry.total_length_ft,
        total_weight_lbs=original_entry.total_weight_lbs,
        total_weight_tons=original_entry.total_weight_tons,
        unit_price_per_cwt=original_entry.unit_price_per_cwt,
        total_price=original_entry.total_price,
        labor_hours=original_entry.labor_hours,
        labor_rate=original_entry.labor_rate,
        labor_cost=original_entry.labor_cost,
        labor_mode=original_entry.labor_mode
    )
    
    db.add(duplicate_entry)
    db.commit()
    db.refresh(duplicate_entry)
    
    return duplicate_entry

@router.post("/projects/{project_id}/save")
async def save_project(
    project_id: str,
    project_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Simple project save - replaces all entries for project in ONE transaction
    No loops, no race conditions, just a clean atomic save
    """
    try:
        # Start transaction
        # Delete existing entries for this project
        deleted_count = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).delete()
        
        # Get entries from request
        entries_data = project_data.get('entries', [])
        
        # Create new entries in batch
        new_entries = []
        for entry_data in entries_data:
            db_entry = TakeoffEntry(
                project_id=project_id,
                qty=entry_data.get('qty', 1),
                shape_key=entry_data.get('shape_key', ''),
                description=entry_data.get('description', ''),
                length_ft=entry_data.get('length_ft', 0.0),
                width_ft=entry_data.get('width_ft', 0.0),
                thickness_in=entry_data.get('thickness_in', 0.0),
                weight_per_ft=entry_data.get('weight_per_ft', 0.0),
                total_length_ft=entry_data.get('total_length_ft', 0.0),
                total_weight_lbs=entry_data.get('total_weight_lbs', 0.0),
                total_weight_tons=entry_data.get('total_weight_tons', 0.0),
                unit_price_per_cwt=entry_data.get('unit_price_per_cwt', 0.0),
                total_price=entry_data.get('total_price', 0.0),
                labor_hours=entry_data.get('labor_hours', 0.0),
                labor_rate=entry_data.get('labor_rate', 0.0),
                labor_cost=entry_data.get('labor_cost', 0.0),
                labor_mode=entry_data.get('labor_mode', 'auto'),
                operations=entry_data.get('operations', []),
                coatings_selected=entry_data.get('coatings_selected', []),
                primary_coating=entry_data.get('primary_coating', ''),
                coating_cost=entry_data.get('coating_cost', 0.0),
                notes=entry_data.get('notes', '')
            )
            new_entries.append(db_entry)
        
        # Add all entries at once
        db.add_all(new_entries)
        db.commit()
        
        return {
            "message": "Project saved successfully",
            "entries_deleted": deleted_count,
            "entries_created": len(new_entries),
            "project_id": project_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save project: {str(e)}")

@router.post("/projects/{project_id}/import-csv")
async def import_takeoff_csv(
    project_id: str,
    # file: UploadFile = File(...),  # Would implement file upload in production
    db: Session = Depends(get_db)
):
    """Import takeoff entries from CSV file (placeholder for Phase 4)"""
    
    return {"message": "CSV import will be implemented in Phase 4"}

@router.get("/projects/{project_id}/export-csv")
async def export_takeoff_csv(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Export takeoff entries to CSV file (placeholder for Phase 4)"""
    
    return {"message": "CSV export will be implemented in Phase 4"}