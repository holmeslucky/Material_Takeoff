"""
Capitol Engineering Company - Proposals API
Non-AI proposal generation using professional templates
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
import io

from app.core.database import get_db
from app.models.takeoff import TakeoffProject, TakeoffEntry
from app.services.proposal_service import ProposalService
from app.services.pdf_service import pdf_service

router = APIRouter()
proposal_service = ProposalService()

class FinalProposalRequest(BaseModel):
    """Request for final proposal after nesting optimization"""
    project_id: str = Field(..., description="Project ID to generate final proposal for")
    nesting_cost: float = Field(..., description="Total material cost from nesting optimization")
    material_markup: float = Field(35.0, description="Material markup percentage")
    coating_markup: float = Field(35.0, description="Coating markup percentage") 
    labor_rate: float = Field(120.0, description="Labor rate per hour")

class FinalProposalResponse(BaseModel):
    """Final proposal response with all costs"""
    project_id: str
    material_cost_base: float
    material_cost_with_markup: float
    labor_cost: float  
    coating_cost: float
    total_cost: float
    total_weight_tons: float
    breakdown: Dict[str, Any]
    summary: str

class PDFRequest(BaseModel):
    """Simple PDF generation request"""
    project_info: Dict[str, Any]
    totals: Dict[str, Any]

@router.options("/generate-pdf")
async def generate_pdf_options():
    """Handle preflight CORS request"""
    return {"status": "ok"}

@router.post("/generate-pdf")
async def generate_proposal_pdf(
    request: PDFRequest
):
    """
    Generate professional proposal PDF
    Returns a PDF file for download
    """
    try:
        # Use the provided data directly
        proposal_data = {
            'project_info': request.project_info,
            'totals': request.totals
        }
        
        # Generate PDF
        pdf_bytes = pdf_service.generate_proposal_pdf(proposal_data)
        
        # Return PDF as response
        project_name = request.project_info.get('name', 'Project')
        filename = f"Capitol_Engineering_Proposal_{project_name.replace(' ', '_')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.post("/generate-final", response_model=FinalProposalResponse)
async def generate_final_proposal(
    request: FinalProposalRequest,
    db: Session = Depends(get_db)
):
    """
    Generate final proposal after nesting optimization
    Combines nesting material costs + labor + coatings with proper markups
    """
    
    # Get project
    project = db.query(TakeoffProject).filter(TakeoffProject.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all takeoff entries to calculate labor and coatings
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == request.project_id).all()
    if not entries:
        raise HTTPException(status_code=400, detail="Project has no takeoff entries")
    
    # Calculate totals from takeoff entries
    total_labor_hours = 0.0
    total_labor_cost = 0.0
    total_coating_cost = 0.0
    total_weight_tons = 0.0
    
    for entry in entries:
        # Labor costs
        labor_hours = float(entry.labor_hours) if entry.labor_hours else 0.0
        labor_cost = float(entry.labor_cost) if entry.labor_cost else 0.0
        
        # If no labor cost but has hours, calculate at $120/hour
        if labor_hours > 0 and labor_cost == 0:
            labor_cost = labor_hours * request.labor_rate
        
        total_labor_hours += labor_hours
        total_labor_cost += labor_cost
        
        # Coating costs
        coating_cost = float(entry.coating_cost) if entry.coating_cost else 0.0
        total_coating_cost += coating_cost
        
        # Total weight
        weight_tons = float(entry.total_weight_tons) if entry.total_weight_tons else 0.0
        total_weight_tons += weight_tons
    
    # Apply markups
    material_cost_base = request.nesting_cost
    material_cost_with_markup = material_cost_base * (1 + request.material_markup / 100)
    coating_cost_with_markup = total_coating_cost * (1 + request.coating_markup / 100)
    
    # Total cost
    total_cost = material_cost_with_markup + total_labor_cost + coating_cost_with_markup
    
    # Create breakdown
    breakdown = {
        "material_base": material_cost_base,
        "material_markup_percent": request.material_markup,
        "material_with_markup": material_cost_with_markup,
        "labor_hours": total_labor_hours,
        "labor_rate": request.labor_rate,
        "labor_cost": total_labor_cost,
        "coating_base": total_coating_cost,
        "coating_markup_percent": request.coating_markup,
        "coating_with_markup": coating_cost_with_markup,
        "total_weight_tons": total_weight_tons,
        "entry_count": len(entries)
    }
    
    # Create summary
    summary = f"""FINAL PROPOSAL - {project.name}
    
Materials (with {request.material_markup}% markup): ${material_cost_with_markup:,.2f}
Labor ({total_labor_hours:.1f} hours @ ${request.labor_rate}/hr): ${total_labor_cost:,.2f}  
Coatings (with {request.coating_markup}% markup): ${coating_cost_with_markup:,.2f}

TOTAL PROJECT COST: ${total_cost:,.2f}"""
    
    return FinalProposalResponse(
        project_id=request.project_id,
        material_cost_base=material_cost_base,
        material_cost_with_markup=material_cost_with_markup,
        labor_cost=total_labor_cost,
        coating_cost=coating_cost_with_markup,
        total_cost=total_cost,
        total_weight_tons=total_weight_tons,
        breakdown=breakdown,
        summary=summary
    )

class MaterialPriceUpdate(BaseModel):
    """Material price update for proposal generation"""
    shape_key: str
    price_per_lb: float
    price_per_ft: Optional[float] = None
    is_edited: bool = False

class ProposalGenerationRequest(BaseModel):
    """Request for CE proposal generation"""
    project_id: str = Field(..., description="Project ID to generate proposal for")
    template_type: str = Field("standard", description="Proposal template: standard, detailed, summary")
    markup_percentage: float = Field(15.0, description="Markup percentage to apply", ge=0, le=50)
    include_labor: bool = Field(True, description="Include labor costs in proposal")
    material_prices: List[MaterialPriceUpdate] = Field([], description="Updated material prices")
    notes: Optional[str] = Field(None, description="Additional project notes")

class ProposalResponse(BaseModel):
    """Response from proposal generation"""
    proposal_content: str
    project_info: Dict[str, Any]
    totals: Dict[str, Any]
    generated_at: str
    template_type: str
    success: bool = True
    message: Optional[str] = None

@router.post("/generate", response_model=ProposalResponse)
async def generate_ce_proposal(
    request: ProposalGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate professional CE proposal without AI
    Uses Capitol Engineering templates and branding
    """
    
    # Get project data
    project = db.query(TakeoffProject).filter(
        TakeoffProject.id == request.project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get takeoff entries
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == request.project_id
    ).all()
    
    if not entries:
        raise HTTPException(status_code=400, detail="Project has no takeoff entries")
    
    # Convert project to dict format
    project_data = {
        'id': project.id,
        'name': project.name,
        'client_name': project.client_name,
        'project_location': project.project_location,
        'description': project.description,
        'is_active': project.is_active,
        'quote_number': project.quote_number,
        'estimator': project.estimator,
        'project_date': project.project_date.isoformat() if project.project_date else None,
        'created_at': project.created_at.isoformat()
    }
    
    # Convert entries to dict format and apply price updates if provided
    entry_dicts = []
    price_updates = {update.shape_key: update for update in request.material_prices}
    
    for entry in entries:
        entry_dict = {
            'id': entry.id,
            'qty': entry.qty,
            'shape_key': entry.shape_key,
            'description': entry.description,
            'length_ft': entry.length_ft,
            'length_in': getattr(entry, 'length_in', 0) or 0,
            'width_in': getattr(entry, 'width_in', 0) or 0,
            'thickness_in': getattr(entry, 'thickness_in', 0) or 0,
            'total_weight_tons': entry.total_weight_tons,
            'total_weight_lbs': entry.total_weight_tons * 2000 if entry.total_weight_tons else 0,
            'labor_hours': entry.labor_hours or 0,
            'labor_cost': entry.labor_cost or 0,
            'category': entry.material.category if entry.material else 'Steel'
        }
        
        # Apply price updates if provided
        if entry.shape_key in price_updates:
            price_update = price_updates[entry.shape_key]
            # Recalculate total_price based on updated price per lb
            weight_lbs = entry_dict['total_weight_lbs']
            entry_dict['total_price'] = weight_lbs * price_update.price_per_lb
            entry_dict['price_per_lb'] = price_update.price_per_lb
            entry_dict['price_per_ft'] = price_update.price_per_ft or 0
        else:
            # Use existing prices
            entry_dict['total_price'] = float(entry.total_price) if entry.total_price else 0
            # Calculate price per lb from CWT
            price_per_lb = float(entry.unit_price_per_cwt) / 100.0 if entry.unit_price_per_cwt else 0.67
            price_per_ft = price_per_lb * entry.weight_per_ft if entry.weight_per_ft else 0
            entry_dict['price_per_lb'] = price_per_lb
            entry_dict['price_per_ft'] = price_per_ft
        
        entry_dicts.append(entry_dict)
    
    try:
        # Generate proposal using the service
        proposal_result = proposal_service.generate_proposal(
            project_data=project_data,
            entries=entry_dicts,
            template_type=request.template_type,
            markup_percentage=request.markup_percentage,
            include_labor=request.include_labor,
            notes=request.notes
        )
        
        return ProposalResponse(
            proposal_content=proposal_result['proposal_content'],
            project_info=proposal_result['project_info'],
            totals=proposal_result['totals'],
            generated_at=proposal_result['generated_at'],
            template_type=proposal_result['template_type'],
            success=True,
            message="Proposal generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate proposal: {str(e)}"
        )

@router.get("/templates")
async def get_proposal_templates():
    """
    Get available proposal templates
    """
    return {
        "templates": [
            {
                "id": "standard",
                "name": "Standard Proposal",
                "description": "Professional proposal with material breakdown and pricing"
            },
            {
                "id": "detailed", 
                "name": "Detailed Proposal",
                "description": "Comprehensive proposal with full material specifications"
            },
            {
                "id": "summary",
                "name": "Executive Summary", 
                "description": "Concise proposal focused on key costs and timeline"
            }
        ]
    }

@router.post("/preview")
async def preview_proposal_totals(
    request: ProposalGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Preview proposal totals without generating full content
    Useful for price confirmation before full proposal generation
    """
    
    # Get project entries
    entries = db.query(TakeoffEntry).filter(
        TakeoffEntry.project_id == request.project_id
    ).all()
    
    if not entries:
        raise HTTPException(status_code=400, detail="Project has no takeoff entries")
    
    # Calculate totals with price updates
    total_material_cost = 0
    total_labor_cost = 0
    total_weight_tons = 0
    total_entries = len(entries)
    
    price_updates = {update.shape_key: update for update in request.material_prices}
    
    for entry in entries:
        # Calculate material cost
        if entry.shape_key in price_updates:
            price_update = price_updates[entry.shape_key]
            weight_lbs = entry.total_weight_tons * 2000 if entry.total_weight_tons else 0
            material_cost = weight_lbs * price_update.price_per_lb
        else:
            material_cost = float(entry.total_price) if entry.total_price else 0
        
        total_material_cost += material_cost
        
        # Add labor cost if included
        if request.include_labor:
            total_labor_cost += float(entry.labor_cost) if entry.labor_cost else 0
            
        total_weight_tons += entry.total_weight_tons or 0
    
    # Apply markup
    material_with_markup = total_material_cost * (1 + request.markup_percentage / 100)
    labor_with_markup = total_labor_cost * (1 + request.markup_percentage / 100) if request.include_labor else 0
    total_with_markup = material_with_markup + labor_with_markup
    
    return {
        "totals": {
            "material_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "markup_percentage": request.markup_percentage,
            "material_with_markup": material_with_markup,
            "labor_with_markup": labor_with_markup,
            "total_cost": total_with_markup,
            "total_weight_tons": total_weight_tons,
            "total_entries": total_entries
        },
        "price_updates_applied": len(request.material_prices),
        "template_type": request.template_type
    }

@router.post("/update-prices")
async def update_material_prices(
    project_id: str,
    price_updates: List[MaterialPriceUpdate],
    db: Session = Depends(get_db)
):
    """
    Update material prices for a project
    This updates the takeoff entries with new pricing
    """
    
    # Verify project exists
    project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get entries to update
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
    if not entries:
        raise HTTPException(status_code=400, detail="Project has no entries to update")
    
    # Create lookup for price updates
    price_lookup = {update.shape_key: update for update in price_updates}
    
    updated_entries = 0
    total_cost_change = 0
    
    try:
        for entry in entries:
            if entry.shape_key in price_lookup:
                price_update = price_lookup[entry.shape_key]
                
                # Calculate new price
                old_price = float(entry.total_price) if entry.total_price else 0
                weight_lbs = entry.total_weight_tons * 2000 if entry.total_weight_tons else 0
                new_total_price = weight_lbs * price_update.price_per_lb
                
                # Update entry - convert back to CWT pricing
                entry.unit_price_per_cwt = price_update.price_per_lb * 100.0
                entry.total_price = new_total_price
                
                total_cost_change += (new_total_price - old_price)
                updated_entries += 1
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Updated prices for {updated_entries} entries",
            "updated_entries": updated_entries,
            "total_cost_change": total_cost_change,
            "project_id": project_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update prices: {str(e)}")

@router.get("/material-prices/{project_id}")
async def get_project_material_prices(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current material prices for a project
    Returns aggregated material data for price review
    """
    
    # Verify project exists
    project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get entries
    entries = db.query(TakeoffEntry).filter(TakeoffEntry.project_id == project_id).all()
    if not entries:
        return {"material_prices": [], "project_id": project_id}
    
    # Group by shape_key
    materials_map = {}
    
    for entry in entries:
        key = entry.shape_key
        if key in materials_map:
            existing = materials_map[key]
            existing["total_qty"] += entry.qty
            existing["total_weight_lbs"] += entry.total_weight_tons * 2000 if entry.total_weight_tons else 0
            existing["total_cost"] += float(entry.total_price) if entry.total_price else 0
        else:
            # Calculate price per lb from CWT price (CWT = price per 100 lbs)
            price_per_lb = float(entry.unit_price_per_cwt) / 100.0 if entry.unit_price_per_cwt else 0.67
            price_per_ft = price_per_lb * entry.weight_per_ft if entry.weight_per_ft else 0
            
            materials_map[key] = {
                "shape_key": entry.shape_key,
                "description": entry.description,
                "category": entry.material.category if entry.material else "Steel",
                "price_per_lb": price_per_lb,
                "price_per_ft": price_per_ft,
                "total_qty": entry.qty,
                "total_weight_lbs": entry.total_weight_tons * 2000 if entry.total_weight_tons else 0,
                "total_cost": float(entry.total_price) if entry.total_price else 0,
                "is_edited": False
            }
    
    return {
        "material_prices": list(materials_map.values()),
        "project_id": project_id,
        "total_materials": len(materials_map)
    }

# Indirect Expenses Models and Endpoints

class IndirectExpensesRequest(BaseModel):
    """Request to save indirect expenses settings"""
    project_id: str
    consumables_percentage: float = Field(default=6.0, description="Consumables percentage")
    misc_percentage: float = Field(default=1.0, description="Miscellaneous percentage")
    fuel_surcharge_percentage: float = Field(default=1.3, description="Fuel surcharge percentage")
    total_indirect_percentage: float = Field(default=8.3, description="Total indirect percentage")
    custom_categories: List[Dict[str, Any]] = Field(default_factory=list, description="Custom indirect categories")

class BidSummaryRequest(BaseModel):
    """Request for bid summary with indirect expenses"""
    project_id: str
    material_cost_base: float
    material_cost_with_markup: float
    labor_cost: float
    coating_cost: float
    indirect_expenses: IndirectExpensesRequest

class BidSummaryResponse(BaseModel):
    """Response with complete bid summary including indirect expenses"""
    project_id: str
    base_costs: Dict[str, float]
    indirect_expenses: Dict[str, float]
    final_totals: Dict[str, float]
    cost_breakdown_percentages: Dict[str, float]
    success: bool

@router.post("/save-indirect-settings")
async def save_indirect_settings(
    request: IndirectExpensesRequest,
    db: Session = Depends(get_db)
):
    """Save indirect expenses settings to project metadata"""
    try:
        project = db.query(TakeoffProject).filter(TakeoffProject.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing metadata or create new
        metadata = project.project_metadata or {}
        
        # Update indirect expenses
        metadata["indirect_expenses"] = {
            "consumables_percentage": request.consumables_percentage,
            "misc_percentage": request.misc_percentage,
            "fuel_surcharge_percentage": request.fuel_surcharge_percentage,
            "total_indirect_percentage": request.total_indirect_percentage,
            "custom_categories": request.custom_categories
        }
        
        project.project_metadata = metadata
        db.commit()
        
        return {"success": True, "message": "Indirect expenses settings saved"}
        
    except Exception as e:
        print(f"Error saving indirect settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save indirect settings: {str(e)}")

@router.get("/indirect-settings/{project_id}")
async def get_indirect_settings(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get indirect expenses settings for a project"""
    try:
        project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        metadata = project.project_metadata or {}
        indirect_expenses = metadata.get("indirect_expenses", {
            "consumables_percentage": 6.0,
            "misc_percentage": 1.0,
            "fuel_surcharge_percentage": 1.3,
            "total_indirect_percentage": 8.3,
            "custom_categories": []
        })
        
        return {
            "project_id": project_id,
            "indirect_expenses": indirect_expenses,
            "success": True
        }
        
    except Exception as e:
        print(f"Error getting indirect settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get indirect settings: {str(e)}")

@router.post("/calculate-with-indirects", response_model=BidSummaryResponse)
async def calculate_bid_with_indirects(
    request: BidSummaryRequest,
    db: Session = Depends(get_db)
):
    """Calculate final bid totals including indirect expenses"""
    try:
        # Base costs from the request
        base_costs = {
            "material_base": request.material_cost_base,
            "material_with_markup": request.material_cost_with_markup,
            "labor": request.labor_cost,
            "coating": request.coating_cost
        }
        
        # Calculate subtotal for percentage-based indirects (excluding base material to avoid double counting)
        subtotal_for_indirects = request.material_cost_with_markup + request.labor_cost + request.coating_cost
        
        # Calculate indirect expenses
        indirect_expenses = {
            "consumables": subtotal_for_indirects * (request.indirect_expenses.consumables_percentage / 100),
            "misc": subtotal_for_indirects * (request.indirect_expenses.misc_percentage / 100),
            "fuel_surcharge": subtotal_for_indirects * (request.indirect_expenses.fuel_surcharge_percentage / 100)
        }
        
        # Add custom categories
        for category in request.indirect_expenses.custom_categories:
            if category.get("type") == "fixed":
                indirect_expenses[category["name"]] = category["value"]
            elif category.get("type") == "percentage":
                indirect_expenses[category["name"]] = subtotal_for_indirects * (category["value"] / 100)
        
        total_indirects = sum(indirect_expenses.values())
        
        # Calculate final totals
        final_total = subtotal_for_indirects + total_indirects
        
        final_totals = {
            "subtotal": subtotal_for_indirects,
            "total_indirects": total_indirects,
            "final_bid_total": final_total
        }
        
        # Calculate percentages
        cost_breakdown_percentages = {}
        if final_total > 0:
            for key, value in base_costs.items():
                cost_breakdown_percentages[key] = (value / final_total) * 100
            for key, value in indirect_expenses.items():
                cost_breakdown_percentages[f"indirect_{key}"] = (value / final_total) * 100
            cost_breakdown_percentages["total_indirects"] = (total_indirects / final_total) * 100
        
        # Save the calculation to project metadata
        await save_indirect_settings(request.indirect_expenses, db)
        
        return BidSummaryResponse(
            project_id=request.project_id,
            base_costs=base_costs,
            indirect_expenses=indirect_expenses,
            final_totals=final_totals,
            cost_breakdown_percentages=cost_breakdown_percentages,
            success=True
        )
        
    except Exception as e:
        print(f"Error calculating bid with indirects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate bid with indirects: {str(e)}")

@router.get("/indirect-defaults")
async def get_indirect_defaults():
    """Get company default indirect expense rates"""
    return {
        "defaults": {
            "consumables_percentage": 6.0,
            "misc_percentage": 1.0,
            "fuel_surcharge_percentage": 1.3,
            "total_indirect_percentage": 8.3,
            "custom_categories": []
        },
        "success": True
    }