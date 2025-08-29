"""
Capitol Engineering Company - Material Nesting & Optimization API
AI-powered material optimization endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

from app.core.database import get_db
from app.models.takeoff import TakeoffEntry, TakeoffProject
from app.services.nesting_service import nesting_service, MaterialPurchase, NestingResult

router = APIRouter()

class NestingOptimizationRequest(BaseModel):
    """Request for material nesting optimization"""
    project_id: str = Field(..., description="Project ID to optimize materials for")
    include_waste_costs: bool = Field(True, description="Include waste costs in calculations")
    optimization_level: str = Field("standard", description="Optimization level: basic, standard, advanced")

class MaterialPurchaseResponse(BaseModel):
    """Material purchase recommendation response"""
    shape_key: str
    size_description: str
    pieces_needed: int
    total_cost: float
    waste_percentage: float
    waste_cost: float
    cuts_count: int

class NestingOptimizationResponse(BaseModel):
    """Response from material nesting optimization"""
    project_id: str
    material_purchases: List[MaterialPurchaseResponse]
    total_waste_percentage: float
    total_cost: float
    cost_savings: float
    optimization_summary: str
    recommendations: List[str]

@router.post("/optimize", response_model=NestingOptimizationResponse)
async def optimize_project_materials(
    request: NestingOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize material purchasing for a project to minimize waste
    Returns comprehensive material purchase recommendations
    """
    
    try:
        # Get project with better error handling
        project = db.query(TakeoffProject).filter(TakeoffProject.id == request.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project with ID '{request.project_id}' not found")
        
        # Get takeoff entries with validation
        entries = db.query(TakeoffEntry).filter(
            TakeoffEntry.project_id == request.project_id
        ).all()
        
        if not entries:
            raise HTTPException(
                status_code=400, 
                detail=f"Project '{project.name}' has no takeoff entries to optimize. Please add entries first."
            )
        
        # Validate entries have required data for optimization
        valid_entries = []
        skipped_entries = 0
        
        for entry in entries:
            # Check if entry has minimum required data
            if (entry.shape_key and 
                entry.qty and entry.qty > 0 and
                entry.length_ft and entry.length_ft > 0 and
                entry.total_weight_tons and entry.total_weight_tons > 0):
                valid_entries.append(entry)
            else:
                skipped_entries += 1
        
        if not valid_entries:
            raise HTTPException(
                status_code=400,
                detail=f"No valid entries found for optimization. All {len(entries)} entries are missing required data (shape_key, qty > 0, length_ft > 0, weight > 0)."
            )
        
        if skipped_entries > 0:
            print(f"Warning: Skipped {skipped_entries} invalid entries during optimization")
        
        entries = valid_entries
    
        # Convert entries to dictionaries for the service with validation
        entry_dicts = []
        conversion_errors = []
        
        for entry in entries:
            try:
                entry_dict = {
                    'id': entry.id,
                    'qty': int(entry.qty) if entry.qty else 1,
                    'shape_key': str(entry.shape_key).strip(),
                    'length_ft': float(entry.length_ft) if entry.length_ft else 0.0,
                    'length_in': float(getattr(entry, 'length_in', 0) or 0),
                    'width_in': float(getattr(entry, 'width_in', 0) or 0),
                    'thickness_in': float(getattr(entry, 'thickness_in', 0) or 0),
                    'total_price': float(entry.total_price) if entry.total_price else 0.0,
                    'description': str(entry.description) if entry.description else ""
                }
                entry_dicts.append(entry_dict)
            except (ValueError, TypeError, AttributeError) as e:
                conversion_errors.append(f"Entry {entry.id}: {str(e)}")
        
        if conversion_errors:
            print(f"Warning: Data conversion errors for {len(conversion_errors)} entries: {conversion_errors}")
        
        if not entry_dicts:
            raise HTTPException(
                status_code=400,
                detail="No entries could be processed due to data conversion errors. Please check your entry data."
            )
        
        # Run optimization with enhanced error handling
        optimization_result = nesting_service.optimize_project_materials(
            takeoff_entries=entry_dicts,
            project_id=request.project_id
        )
        
        if not optimization_result:
            raise HTTPException(
                status_code=500,
                detail="Optimization service returned no results. Please check your project data."
            )
        
        if not optimization_result.material_purchases:
            raise HTTPException(
                status_code=400,
                detail="No material purchase recommendations generated. This could be due to unsupported material types or invalid dimensions."
            )
        
        # Convert result to response format with validation
        purchase_responses = []
        for i, purchase in enumerate(optimization_result.material_purchases):
            try:
                purchase_response = MaterialPurchaseResponse(
                    shape_key=purchase.shape_key or f"unknown_{i}",
                    size_description=purchase.size_description or "Unknown Size",
                    pieces_needed=max(1, purchase.pieces_needed),  # Ensure at least 1 piece
                    total_cost=float(purchase.total_cost) if purchase.total_cost else 0.0,
                    waste_percentage=min(100.0, max(0.0, purchase.waste_percentage)),  # Clamp between 0-100
                    waste_cost=float(purchase.waste_cost) if purchase.waste_cost else 0.0,
                    cuts_count=len(purchase.cuts_from_this_size) if purchase.cuts_from_this_size else 0
                )
                purchase_responses.append(purchase_response)
            except Exception as e:
                print(f"Warning: Could not convert purchase recommendation {i}: {str(e)}")
                continue
        
        if not purchase_responses:
            raise HTTPException(
                status_code=500,
                detail="Could not format any purchase recommendations. Please check the optimization data."
            )
        
        # Generate recommendations based on results
        recommendations = _generate_recommendations(optimization_result)
        
        # Calculate cost savings more accurately
        original_cost = sum(float(entry.get('total_price', 0)) for entry in entry_dicts)
        optimized_cost = float(optimization_result.total_cost)
        actual_savings = max(0, original_cost - optimized_cost)
        
        return NestingOptimizationResponse(
            project_id=request.project_id,
            material_purchases=purchase_responses,
            total_waste_percentage=min(100.0, max(0.0, optimization_result.total_waste_percentage)),
            total_cost=optimized_cost,
            cost_savings=actual_savings,
            optimization_summary=optimization_result.optimization_summary or "Optimization completed successfully",
            recommendations=recommendations or ["No specific recommendations"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Nesting optimization error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed due to an unexpected error: {str(e)}. Please check your project data and try again."
        )

class SingleEntryOptimizationRequest(BaseModel):
    """Request for optimizing a single takeoff entry"""
    entry: dict = Field(..., description="Single takeoff entry to optimize")
    optimization_level: str = Field("standard", description="Optimization level: basic, standard, advanced")

class SingleEntryOptimizationResponse(BaseModel):
    """Response for single entry optimization"""
    optimized_cost: float
    waste_percentage: float
    waste_cost: float
    purchase_size: str
    cuts_from_size: int
    material_utilization: float
    supplier: str
    lead_time: str
    efficiency_grade: str  # A, B, C, D rating
    alternative_suggestions: List[str]

@router.post("/optimize-entry", response_model=SingleEntryOptimizationResponse)
async def optimize_single_entry(
    request: SingleEntryOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize a single takeoff entry for real-time feedback
    Returns optimization data for enhanced table display
    """
    
    try:
        # Validate entry data
        if not request.entry:
            raise HTTPException(status_code=400, detail="Entry data is required")
        
        # Check required fields
        required_fields = ['shape_key', 'qty', 'length_ft']
        missing_fields = [field for field in required_fields if not request.entry.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate field values
        if request.entry.get('qty', 0) <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        if request.entry.get('length_ft', 0) <= 0:
            raise HTTPException(status_code=400, detail="Length must be greater than 0")
        
        # Convert single entry to list for the service with validation
        entry_data = {
            'id': request.entry.get('id', 'single_entry'),
            'qty': int(request.entry.get('qty', 1)),
            'shape_key': str(request.entry.get('shape_key', '')).strip(),
            'length_ft': float(request.entry.get('length_ft', 0)),
            'length_in': float(request.entry.get('length_in', 0)),
            'width_in': float(request.entry.get('width_in', 0)),
            'thickness_in': float(request.entry.get('thickness_in', 0)),
            'total_price': float(request.entry.get('total_price', 0)),
            'description': str(request.entry.get('description', ''))
        }
        
        entry_list = [entry_data]
        
        # Run optimization
        optimization_result = nesting_service.optimize_project_materials(
            takeoff_entries=entry_list,
            project_id="single_entry"
        )
        
        if not optimization_result:
            raise HTTPException(
                status_code=500, 
                detail="Optimization service returned no results"
            )
        
        if not optimization_result.material_purchases:
            raise HTTPException(
                status_code=400, 
                detail="Unable to optimize entry - no purchase recommendations generated. This may be due to an unsupported material type or invalid dimensions."
            )
        
        # Get the first (and only) purchase recommendation
        purchase = optimization_result.material_purchases[0]
        
        # Calculate efficiency grade
        efficiency_grade = _calculate_efficiency_grade(purchase.waste_percentage)
        
        # Generate alternative suggestions
        alternatives = _generate_alternatives(request.entry, purchase)
        
        return SingleEntryOptimizationResponse(
            optimized_cost=float(purchase.total_cost) if purchase.total_cost else 0.0,
            waste_percentage=min(100.0, max(0.0, purchase.waste_percentage)),
            waste_cost=float(purchase.waste_cost) if purchase.waste_cost else 0.0,
            purchase_size=purchase.size_description or "Unknown Size",
            cuts_from_size=len(purchase.cuts_from_this_size) if purchase.cuts_from_this_size else 1,
            material_utilization=max(0.0, min(100.0, 100 - purchase.waste_percentage)),
            supplier=getattr(purchase.standard_size, 'supplier', None) or "Standard Supply",
            lead_time="2-3 days",
            efficiency_grade=efficiency_grade,
            alternative_suggestions=alternatives or ["No specific alternatives available"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entry data: {str(e)}"
        )
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Single entry optimization error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Entry optimization failed: {str(e)}"
        )

@router.get("/standard-sizes")
async def get_standard_material_sizes():
    """Get available standard material sizes for optimization based on actual inventory"""
    
    return {
        "plate_sizes": [
            {"width_in": 36, "length_ft": 8, "description": "36\" × 96\" (3'×8')"},
            {"width_in": 48, "length_ft": 8, "description": "48\" × 96\" (4'×8')"},
            {"width_in": 48, "length_ft": 10, "description": "48\" × 120\" (4'×10')"},
            {"width_in": 60, "length_ft": 10, "description": "60\" × 120\" (5'×10')"},
            {"width_in": 60, "length_ft": 12, "description": "60\" × 144\" (5'×12')"},
            {"width_in": 72, "length_ft": 12, "description": "72\" × 144\" (6'×12')"},
            {"width_in": 72, "length_ft": 20, "description": "72\" × 240\" (6'×20') — less common"},
            {"width_in": 96, "length_ft": 20, "description": "96\" × 240\" (8'×20')"},
            {"width_in": 96, "length_ft": 24, "description": "96\" × 288\" (8'×24') — mill/large service centers"}
        ],
        "material_lengths": {
            "structural": [20, 40, 60],  # Angles, Channels, Beams
            "hss_tube": [20, 24, 40],    # HSS (square/rectangular)
            "pipe": [21, 40],            # Pipe - single/double random
            "bar": [12, 20]              # Flat/Round/Square Bar
        },
        "thickness_options": [0.1875, 0.25, 0.3125, 0.375, 0.5, 0.625, 0.75, 1.0, 1.25, 1.5, 2.0],
        "standard_suppliers": ["Standard Supply", "Mill/Large Service Center", "Steel Warehouse"]
    }

@router.get("/waste-analysis/{project_id}")
async def analyze_material_waste(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Analyze current material waste for a project
    Shows potential savings from optimization
    """
    
    try:
        # Validate project exists
        project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=404, 
                detail=f"Project with ID '{project_id}' not found"
            )
        
        # Get current takeoff entries
        entries = db.query(TakeoffEntry).filter(
            TakeoffEntry.project_id == project_id
        ).all()
        
        if not entries:
            raise HTTPException(
                status_code=404, 
                detail=f"No takeoff entries found for project '{project.name}'"
            )
        
        # Filter valid entries for analysis
        valid_entries = []
        for entry in entries:
            if (entry.shape_key and 
                entry.qty and entry.qty > 0 and
                entry.length_ft and entry.length_ft > 0 and
                entry.total_price):
                valid_entries.append(entry)
        
        if not valid_entries:
            return {
                "project_id": project_id,
                "project_name": project.name,
                "current_material_cost": 0.0,
                "optimized_material_cost": 0.0,
                "potential_savings": 0.0,
                "savings_percentage": 0.0,
                "total_waste_percentage": 0.0,
                "optimization_feasible": False,
                "message": f"No valid entries found for analysis. {len(entries)} entries were skipped due to missing or invalid data."
            }
        
        # Calculate current material costs (without optimization)
        current_total = 0.0
        calculation_errors = []
        
        for entry in valid_entries:
            try:
                price = float(entry.total_price) if entry.total_price else 0.0
                current_total += price
            except (ValueError, TypeError) as e:
                calculation_errors.append(f"Entry {entry.id}: {str(e)}")
        
        if calculation_errors:
            print(f"Warning: Price calculation errors: {calculation_errors}")
        
        # Get optimized costs with better error handling
        entry_dicts = []
        for entry in valid_entries:
            try:
                entry_dict = {
                    'id': entry.id,
                    'qty': int(entry.qty),
                    'shape_key': str(entry.shape_key).strip(),
                    'length_ft': float(entry.length_ft),
                    'length_in': float(getattr(entry, 'length_in', 0) or 0),
                    'width_in': float(getattr(entry, 'width_in', 0) or 0),
                    'thickness_in': float(getattr(entry, 'thickness_in', 0) or 0),
                    'total_price': float(entry.total_price) if entry.total_price else 0.0
                }
                entry_dicts.append(entry_dict)
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not process entry {entry.id} for waste analysis: {str(e)}")
                continue
        
        if not entry_dicts:
            raise HTTPException(
                status_code=400,
                detail="No entries could be processed for waste analysis due to data conversion errors"
            )
        
        optimization_result = nesting_service.optimize_project_materials(
            takeoff_entries=entry_dicts,
            project_id=project_id
        )
        
        if not optimization_result:
            raise HTTPException(
                status_code=500,
                detail="Optimization service failed to return results for waste analysis"
            )
        
        optimized_total = float(optimization_result.total_cost) if optimization_result.total_cost else 0.0
        potential_savings = max(0, current_total - optimized_total)
        savings_percentage = (potential_savings / current_total) * 100 if current_total > 0 else 0.0
        waste_percentage = min(100.0, max(0.0, optimization_result.total_waste_percentage)) if optimization_result.total_waste_percentage else 0.0
        
        # Add more detailed analysis
        material_breakdown = {}
        if optimization_result.material_purchases:
            for purchase in optimization_result.material_purchases:
                material_type = purchase.shape_key or "Unknown"
                if material_type not in material_breakdown:
                    material_breakdown[material_type] = {
                        "pieces": 0,
                        "cost": 0.0,
                        "waste_percentage": 0.0
                    }
                material_breakdown[material_type]["pieces"] += purchase.pieces_needed or 0
                material_breakdown[material_type]["cost"] += float(purchase.total_cost) if purchase.total_cost else 0.0
                material_breakdown[material_type]["waste_percentage"] = max(
                    material_breakdown[material_type]["waste_percentage"],
                    purchase.waste_percentage or 0.0
                )
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "current_material_cost": round(current_total, 2),
            "optimized_material_cost": round(optimized_total, 2),
            "potential_savings": round(potential_savings, 2),
            "savings_percentage": round(savings_percentage, 1),
            "total_waste_percentage": round(waste_percentage, 1),
            "optimization_feasible": potential_savings > 0 and waste_percentage > 5.0,
            "entries_analyzed": len(entry_dicts),
            "entries_total": len(entries),
            "material_breakdown": material_breakdown,
            "analysis_summary": optimization_result.optimization_summary if optimization_result.optimization_summary else "Analysis completed successfully"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Waste analysis error for project {project_id}: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Waste analysis failed: {str(e)}"
        )

def _calculate_efficiency_grade(waste_percentage: float) -> str:
    """Calculate efficiency grade based on waste percentage"""
    if waste_percentage <= 10:
        return "A"
    elif waste_percentage <= 20:
        return "B"
    elif waste_percentage <= 35:
        return "C"
    else:
        return "D"

def _generate_alternatives(entry: dict, current_purchase) -> List[str]:
    """Generate alternative suggestions for better optimization"""
    alternatives = []
    
    if current_purchase.waste_percentage > 30:
        alternatives.append("Consider custom length to reduce waste")
        alternatives.append("Combine with similar cuts from other entries")
    
    if current_purchase.waste_percentage < 5:
        alternatives.append("Excellent efficiency - consider as standard size")
    
    # Add material-specific suggestions
    shape_key = entry.get('shape_key', '').upper()
    if 'PL' in shape_key or 'PLATE' in shape_key:
        alternatives.append("Consider nesting with other plate cuts")
    else:
        alternatives.append("Check for drop utilization opportunities")
    
    return alternatives[:3]  # Limit to 3 suggestions

def _generate_recommendations(optimization_result: NestingResult) -> List[str]:
    """Generate actionable recommendations based on optimization results"""
    recommendations = []
    
    if optimization_result.total_waste_percentage > 25:
        recommendations.append("Consider alternative material sizes to reduce waste above 25%")
    
    if optimization_result.total_waste_percentage < 10:
        recommendations.append("Excellent material utilization - consider using this as a standard approach")
    
    # Check for opportunities to consolidate purchases
    shape_counts = {}
    for purchase in optimization_result.material_purchases:
        shape = purchase.shape_key
        if shape in shape_counts:
            shape_counts[shape] += 1
        else:
            shape_counts[shape] = 1
    
    for shape, count in shape_counts.items():
        if count > 3:
            recommendations.append(f"Consider bulk purchasing for {shape} ({count} different sizes needed)")
    
    # Check for high waste items
    for purchase in optimization_result.material_purchases:
        if purchase.waste_percentage > 40:
            recommendations.append(
                f"High waste on {purchase.size_description} ({purchase.waste_percentage:.1f}%) - "
                "consider custom sizes or alternative cutting patterns"
            )
    
    if not recommendations:
        recommendations.append("Material optimization looks good - no specific recommendations")
    
    return recommendations

@router.post("/save-results/{project_id}")
async def save_nesting_results(
    project_id: str,
    nesting_results: dict,
    db: Session = Depends(get_db)
):
    """
    Save nesting optimization results for a project
    Allows persistence of manual edits and optimized configurations
    """
    
    try:
        # Verify project exists
        project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        # Store nesting results as JSON metadata on the project
        # In production, you'd want a separate nesting_results table
        if not hasattr(project, 'project_metadata'):
            project.project_metadata = {}
        
        project.project_metadata = project.project_metadata or {}
        project.project_metadata['nesting_results'] = nesting_results
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Nesting results saved successfully for project {project_id}",
            "project_id": project_id,
            "saved_at": "now"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error saving nesting results for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save nesting results: {str(e)}"
        )

@router.get("/results/{project_id}")
async def get_nesting_results(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve saved nesting optimization results for a project
    Returns previously saved configurations including manual edits
    """
    
    try:
        # Verify project exists
        project = db.query(TakeoffProject).filter(TakeoffProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        # Get saved nesting results from project metadata
        project_metadata = getattr(project, 'project_metadata', {}) or {}
        nesting_data = project_metadata.get('nesting_results')
        
        if not nesting_data:
            # No saved results found - return empty state
            return {
                "project_id": project_id,
                "has_saved_results": False,
                "message": "No saved nesting results found for this project"
            }
        
        # Return saved results
        return {
            "project_id": project_id,
            "has_saved_results": True,
            **nesting_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving nesting results for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve nesting results: {str(e)}"
        )