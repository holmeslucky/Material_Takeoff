"""
Capitol Engineering Company - Labor Rate Management API
Endpoints for managing custom labor rates and multipliers
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.services.takeoff_service import TakeoffCalculationService

router = APIRouter()
takeoff_service = TakeoffCalculationService()

@router.get("/types")
async def get_labor_types() -> Dict[str, Dict[str, Any]]:
    """
    Get all available custom labor types with multipliers and descriptions
    Returns labor types like Stairs (1.25x), Handrail (1.25x), etc.
    """
    
    return takeoff_service.get_available_labor_types()

@router.post("/calculate")
async def calculate_custom_labor(
    material_key: str,
    qty: int,
    length_ft: float,
    width_ft: float = 0.0,
    labor_type: str = None,
    mode: str = "auto"
) -> Dict[str, Any]:
    """
    Calculate labor hours with custom labor type multipliers
    
    Examples:
    - labor_type="stairs" -> 1.25x multiplier
    - labor_type="handrail" -> 1.25x multiplier  
    - labor_type="welding_complex" -> 1.5x multiplier
    """
    
    try:
        labor_result = takeoff_service.calculate_labor_hours(
            material_key=material_key,
            qty=qty,
            length_ft=length_ft,
            width_ft=width_ft,
            mode=mode,
            labor_type=labor_type
        )
        
        return labor_result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/compare")
async def compare_labor_rates(
    material_key: str,
    qty: int,
    length_ft: float,
    width_ft: float = 0.0,
    labor_types: List[str] = None
) -> Dict[str, Any]:
    """
    Compare labor costs across different labor types
    Useful for showing cost differences between standard, stairs, handrail, etc.
    """
    
    if not labor_types:
        labor_types = ["standard", "stairs", "handrail", "welding_complex"]
    
    comparisons = {}
    
    for labor_type in labor_types:
        try:
            # Use None for standard calculation
            actual_type = None if labor_type == "standard" else labor_type
            
            result = takeoff_service.calculate_labor_hours(
                material_key=material_key,
                qty=qty,
                length_ft=length_ft,
                width_ft=width_ft,
                mode="auto",
                labor_type=actual_type
            )
            
            comparisons[labor_type] = {
                "labor_hours": result["labor_hours"],
                "labor_cost": result["labor_cost"], 
                "custom_multiplier": result["custom_multiplier"],
                "total_multiplier": result["total_multiplier"]
            }
            
        except Exception as e:
            comparisons[labor_type] = {"error": str(e)}
    
    return {
        "material_key": material_key,
        "qty": qty,
        "length_ft": length_ft,
        "width_ft": width_ft,
        "comparisons": comparisons
    }

@router.get("/rates/summary")
async def get_labor_rates_summary() -> Dict[str, Any]:
    """
    Get summary of all labor rates and multipliers for admin interface
    """
    
    available_types = takeoff_service.get_available_labor_types()
    
    # Base labor rate info (from master takeoff)
    base_info = {
        "base_hourly_rate": 120.00,
        "markup": 35.0,
        "handling": 20.0,
        "company": "Capitol Engineering Company",
        "fabrication_type": "Shop Fabrication Only",
        "base_hours_per_ton": {
            "Wide_Flange": 8.0,
            "Plate": 12.0,
            "Angle": 10.0,
            "HSS_Tube": 9.0,
            "Channel": 8.5,
            "Other": 10.0
        },
        "shop_operations": {
            "Fit & Tack": 0.67,
            "Pressbrake Forming": 0.50,
            "Dragon Plasma Cutting": 0.18,
            "Beam Line Cutting": 0.50,
            "Welding": "Variable"
        }
    }
    
    return {
        "base_info": base_info,
        "custom_labor_types": available_types,
        "total_custom_types": len(available_types)
    }