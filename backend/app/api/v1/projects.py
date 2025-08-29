"""
Capitol Engineering Company - Projects API Endpoints
Project management for takeoff system
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.takeoff import TakeoffProject, TakeoffEntry
from app.schemas.takeoff import (
    TakeoffProjectCreate, TakeoffProjectUpdate, TakeoffProjectResponse,
    ProjectTakeoffSaveRequest, ProjectTakeoffSaveResponse
)

router = APIRouter()

@router.get("/", response_model=List[TakeoffProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None, description="Filter by project status"),
    search: str = Query(None, description="Search in project name or client"),
    db: Session = Depends(get_db)
):
    """Get all projects with optional filtering and search"""
    
    query = db.query(TakeoffProject)
    
    # Status filter (using is_active field)
    if status:
        if status.lower() == 'active':
            query = query.filter(TakeoffProject.is_active == True)
        elif status.lower() == 'inactive':
            query = query.filter(TakeoffProject.is_active == False)
    
    # Search filter
    if search:
        search_filter = (
            TakeoffProject.name.ilike(f"%{search}%") |
            TakeoffProject.client_name.ilike(f"%{search}%") |
            TakeoffProject.project_location.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get projects with statistics
    projects = query.offset(skip).limit(limit).all()
    
    # Convert to response format with field mapping
    response_projects = []
    for project in projects:
        # Count entries and calculate totals
        entry_stats = db.query(
            func.count(TakeoffEntry.id).label('total_entries'),
            func.sum(TakeoffEntry.total_weight_tons).label('total_weight_tons'),
            func.sum(TakeoffEntry.total_price).label('total_value')
        ).filter(TakeoffEntry.project_id == project.id).first()
        
        # Create response data with proper field mapping
        response_data = {
            "id": project.id,
            "name": project.name,
            "client": project.client_name,  # Map client_name to client
            "location": project.project_location,  # Map project_location to location
            "description": project.description,
            "status": "active" if project.is_active else "inactive",
            "quote_number": project.quote_number,
            "estimator": project.estimator,
            "project_date": project.project_date,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "total_entries": entry_stats.total_entries or 0,
            "total_weight_tons": float(entry_stats.total_weight_tons or 0),
            "total_value": float(entry_stats.total_value or 0)
        }
        response_projects.append(response_data)
    
    return response_projects

@router.post("/", response_model=TakeoffProjectResponse)
async def create_project(
    project_data: TakeoffProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new takeoff project with manual project ID"""
    
    # Use manual project ID from form input
    project_id = project_data.project_id.strip().upper()
    
    # Check if project ID already exists
    try:
        existing_project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if existing_project:
            raise HTTPException(
                status_code=400, 
                detail=f"Project ID '{project_id}' already exists. Please use a unique project ID."
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Database query failed during ID check: {e}")
        # Continue with the manual ID even if check fails
    
    # Create project
    from datetime import datetime as dt
    project_date = None
    if hasattr(project_data, 'date') and project_data.date:
        try:
            project_date = dt.fromisoformat(project_data.date)
        except:
            project_date = None
    
    db_project = TakeoffProject(
        id=project_id,
        name=project_data.name,
        client_name=project_data.client,
        project_location=project_data.location if hasattr(project_data, 'location') else None,
        description=project_data.description,
        quote_number=project_data.quote_number if hasattr(project_data, 'quote_number') else None,
        estimator=project_data.estimator if hasattr(project_data, 'estimator') else None,
        project_date=project_date
    )
    
    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        print(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")
    
    # Create response manually mapping database fields to response schema
    response_data = {
        "id": db_project.id,
        "name": db_project.name,
        "client": db_project.client_name,
        "location": db_project.project_location,
        "description": db_project.description,
        "status": "active" if db_project.is_active else "inactive",
        "quote_number": db_project.quote_number,
        "estimator": db_project.estimator,
        "project_date": db_project.project_date,
        "created_at": db_project.created_at,
        "updated_at": db_project.updated_at,
        "total_entries": 0,
        "total_weight_tons": 0.0,
        "total_value": 0.0
    }
    
    return response_data

@router.get("/{project_id}", response_model=TakeoffProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get project by ID with statistics"""
    
    project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Add project statistics
    entry_stats = db.query(
        func.count(TakeoffEntry.id).label('total_entries'),
        func.sum(TakeoffEntry.total_weight_tons).label('total_weight_tons'),
        func.sum(TakeoffEntry.total_price).label('total_value')
    ).filter(TakeoffEntry.project_id == project_id).first()
    
    # Create response data with proper field mapping
    response_data = {
        "id": project.id,
        "name": project.name,
        "client": project.client_name,  # Map client_name to client
        "location": project.project_location,  # Map project_location to location
        "description": project.description,
        "status": "active" if project.is_active else "inactive",
        "quote_number": project.quote_number,
        "estimator": project.estimator,
        "project_date": project.project_date,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "total_entries": entry_stats.total_entries or 0,
        "total_weight_tons": float(entry_stats.total_weight_tons or 0),
        "total_value": float(entry_stats.total_value or 0)
    }
    
    return response_data

@router.put("/{project_id}", response_model=TakeoffProjectResponse)
async def update_project(
    project_id: str,
    project_update: TakeoffProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update project information"""
    
    db_project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    for field, value in project_update.dict(exclude_unset=True).items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    # Return properly formatted response
    response_data = {
        "id": db_project.id,
        "name": db_project.name,
        "client": db_project.client_name,
        "location": db_project.project_location,
        "description": db_project.description,
        "status": "active" if db_project.is_active else "inactive",
        "quote_number": db_project.quote_number,
        "estimator": db_project.estimator,
        "project_date": db_project.project_date,
        "created_at": db_project.created_at,
        "updated_at": db_project.updated_at,
        "total_entries": 0,
        "total_weight_tons": 0.0,
        "total_value": 0.0
    }
    
    return response_data

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Delete project and all associated takeoff entries"""
    
    db_project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete associated takeoff entries first
    db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).delete()
    
    # Delete project
    db.delete(db_project)
    db.commit()
    
    return {"message": f"Project {project_id} deleted successfully"}

@router.post("/{project_id}/duplicate")
async def duplicate_project(
    project_id: str,
    new_name: str = Query(..., description="Name for the duplicated project"),
    db: Session = Depends(get_db)
):
    """Duplicate a project with all its takeoff entries"""
    
    original_project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not original_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create new project
    project_data = TakeoffProjectCreate(
        name=new_name,
        client=original_project.client_name,
        location=original_project.project_location,
        description=f"Duplicate of {original_project.name}"
    )
    
    new_project = await create_project(project_data, db)
    
    # Copy takeoff entries
    original_entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
    
    for entry in original_entries:
        duplicate_entry = TakeoffEntry(
            project_id=new_project.id,
            qty=entry.qty,
            shape_key=entry.shape_key,
            description=entry.description,
            length_ft=entry.length_ft,
            width_ft=entry.width_ft,
            weight_per_ft=entry.weight_per_ft,
            total_length_ft=entry.total_length_ft,
            total_weight_lbs=entry.total_weight_lbs,
            total_weight_tons=entry.total_weight_tons,
            unit_price_per_cwt=entry.unit_price_per_cwt,
            total_price=entry.total_price,
            labor_hours=entry.labor_hours,
            labor_rate=entry.labor_rate,
            labor_cost=entry.labor_cost,
            labor_mode=entry.labor_mode
        )
        db.add(duplicate_entry)
    
    db.commit()
    
    return {
        "message": f"Project duplicated successfully",
        "original_project_id": project_id,
        "new_project_id": new_project.id,
        "entries_copied": len(original_entries)
    }

@router.get("/{project_id}/summary")
async def get_project_summary(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed project summary with breakdowns"""
    
    project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all entries for the project
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
    
    # Calculate totals and breakdowns
    total_entries = len(entries)
    total_weight_tons = sum(entry.total_weight_tons for entry in entries)
    total_material_cost = sum(entry.total_price for entry in entries)
    total_labor_hours = sum(entry.labor_hours or 0 for entry in entries)
    total_labor_cost = sum(entry.labor_cost or 0 for entry in entries)
    
    # Category breakdown
    category_breakdown = {}
    for entry in entries:
        # Get material to determine category
        material = entry.material if hasattr(entry, 'material') else None
        category = material.category if material else 'Other'
        
        if category not in category_breakdown:
            category_breakdown[category] = {
                'count': 0,
                'weight_tons': 0.0,
                'material_cost': 0.0,
                'labor_hours': 0.0,
                'labor_cost': 0.0
            }
        
        category_breakdown[category]['count'] += 1
        category_breakdown[category]['weight_tons'] += entry.total_weight_tons
        category_breakdown[category]['material_cost'] += entry.total_price
        category_breakdown[category]['labor_hours'] += entry.labor_hours or 0
        category_breakdown[category]['labor_cost'] += entry.labor_cost or 0
    
    return {
        'project_info': {
            'id': project.id,
            'name': project.name,
            'client': project.client_name,
            'location': project.project_location,
            'status': "active" if project.is_active else "inactive",
            'created_date': project.created_at
        },
        'totals': {
            'total_entries': total_entries,
            'total_weight_tons': round(total_weight_tons, 2),
            'total_material_cost': round(total_material_cost, 2),
            'total_labor_hours': round(total_labor_hours, 1),
            'total_labor_cost': round(total_labor_cost, 2),
            'total_project_cost': round(total_material_cost + total_labor_cost, 2)
        },
        'category_breakdown': category_breakdown,
        'company_info': {
            'name': 'Capitol Engineering Company',
            'address': '724 E Southern Pacific Dr, Phoenix AZ 85034',
            'phone': '602-281-6517',
            'mobile': '951-732-1514',
            'website': 'www.capitolaz.com'
        }
    }

@router.get("/stats/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for all projects"""
    
    # Overall statistics
    total_projects = db.query(func.count(TakeoffProject.id)).scalar()
    
    # Projects by status
    active_count = db.query(func.count(TakeoffProject.id)).filter(TakeoffProject.is_active == True).scalar() or 0
    inactive_count = db.query(func.count(TakeoffProject.id)).filter(TakeoffProject.is_active == False).scalar() or 0
    status_counts = [('active', active_count), ('inactive', inactive_count)]
    
    # Recent projects
    recent_projects = db.query(TakeoffProject).order_by(
        desc(TakeoffProject.created_at)
    ).limit(5).all()
    
    # Total value across all projects
    total_value = db.query(
        func.sum(TakeoffEntry.total_price)
    ).scalar() or 0
    
    # Total weight across all projects
    total_weight = db.query(
        func.sum(TakeoffEntry.total_weight_tons)
    ).scalar() or 0
    
    return {
        'overview': {
            'total_projects': total_projects,
            'total_value': float(total_value),
            'total_weight_tons': float(total_weight),
        },
        'by_status': {status: count for status, count in status_counts},
        'recent_projects': [
            {
                'id': p.id,
                'name': p.name,
                'client': p.client_name,
                'status': "active" if p.is_active else "inactive",
                'created_date': p.created_at
            }
            for p in recent_projects
        ]
    }

@router.get("/{project_id}/test")
async def test_project_route(project_id: str):
    """Test route to verify project parameter works"""
    return {"message": f"Project {project_id} test route works"}

@router.post("/{project_id}/takeoff", response_model=ProjectTakeoffSaveResponse)
async def save_project_takeoff(
    project_id: str,
    request: ProjectTakeoffSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk save/update all takeoff entries for a project
    This endpoint handles the frontend save button functionality  
    """
    
    # Verify project exists
    project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Delete existing entries for this project to avoid duplicates
        db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).delete()
        
        # Create new entries from the request
        entries_saved = 0
        for entry_data in request.entries:
            # Create new TakeoffEntry from the data with proper field mapping
            new_entry = TakeoffEntry(
                project_id=project_id,
                qty=entry_data.get('qty', 1),
                shape_key=entry_data.get('shape_key', ''),
                description=entry_data.get('description', ''),
                length_ft=entry_data.get('length_ft', 0.0),
                width_ft=entry_data.get('width_in', 0.0) / 12.0 if entry_data.get('width_in') else 0.0,  # Convert inches to feet
                weight_per_ft=entry_data.get('weight_per_ft', 0.0),
                total_length_ft=entry_data.get('total_length_ft', 0.0),
                total_weight_lbs=entry_data.get('total_weight_lbs', 0.0),
                total_weight_tons=entry_data.get('total_weight_tons', 0.0),
                unit_price_per_cwt=entry_data.get('unit_price_per_cwt', 0.0),
                total_price=entry_data.get('total_price', 0.0),
                labor_hours=entry_data.get('labor_hours', 0.0),
                labor_rate=entry_data.get('labor_rate', 75.0),
                labor_cost=entry_data.get('labor_cost', 0.0),
                labor_mode=entry_data.get('labor_mode', 'auto'),
                notes=entry_data.get('notes', '')
            )
            
            db.add(new_entry)
            entries_saved += 1
        
        # Commit all changes
        db.commit()
        
        return ProjectTakeoffSaveResponse(
            success=True,
            message=f"Successfully saved {entries_saved} takeoff entries",
            entries_saved=entries_saved,
            project_id=project_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save takeoff entries: {str(e)}"
        )