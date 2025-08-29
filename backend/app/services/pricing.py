from typing import Literal, Optional

LaborMode = Literal["auto", "manual"]

def calculate_labor_hours(material_key: str, qty: float, length_ft: float | None) -> float:
    """
    Calculate labor hours based on material type - matches desktop logic
    """
    base_hours = 0.5  # Default base hours per piece
    
    # Material-specific labor rates (from desktop app)
    if material_key.startswith("W"):  # Wide Flange
        base_hours = 0.75
    elif material_key.startswith("C"):  # Channel
        base_hours = 0.6
    elif "PLATE" in material_key.upper() or material_key.startswith("PL"):  # Plate
        base_hours = 0.4
    elif material_key.startswith("HSS"):  # HSS Tube
        base_hours = 0.6
    elif material_key.startswith("L"):  # Angle
        base_hours = 0.5
    
    # Normalize to 20ft baseline (matches desktop logic)
    length_factor = (length_ft or 20.0) / 20.0
    
    return max(0.0, base_hours * qty * length_factor)

def calculate_plate_weight(
    qty: float, 
    width_in: float, 
    length_ft: float, 
    length_in: float, 
    thickness_in: float
) -> float:
    """
    Calculate plate weight using area-based calculation - matches desktop logic
    """
    # Convert total length to feet
    total_length_ft = length_ft + (length_in / 12)
    
    # Calculate area in square feet
    area_sqft = (width_in * total_length_ft * 12) / 144
    
    # Steel plate weight: 40.8 lbs per cubic foot (matches desktop)
    plate_weight_per_sqft = thickness_in * 40.8 / 12  # Convert thickness to feet
    
    return qty * area_sqft * plate_weight_per_sqft

def parse_plate_thickness(shape_key: str) -> float:
    """
    Parse thickness from plate shape key - matches desktop logic
    Examples: PL1/2 = 0.5", PL3/4 = 0.75", PL1 = 1.0"
    """
    thickness_str = shape_key.replace("PL", "").replace("PLATE", "").strip()
    
    if "/" in thickness_str:
        # Handle fractions like "1/2"
        parts = thickness_str.split("/")
        return float(parts[0]) / float(parts[1])
    elif "-" in thickness_str:
        # Handle complex formats like "1-1/4"
        parts = thickness_str.split("-")
        if len(parts) == 2 and "/" in parts[1]:
            frac_parts = parts[1].split("/")
            return float(parts[0]) + float(frac_parts[0]) / float(frac_parts[1])
        else:
            return float(parts[0])
    else:
        # Handle simple decimals
        try:
            return float(thickness_str) if thickness_str.replace(".", "").isdigit() else 0.5
        except ValueError:
            return 0.5  # Default thickness

def calculate_totals(material_cost: float, labor_cost: float) -> dict:
    """
    Calculate final totals with consumables and markup - matches desktop logic
    """
    consumables = material_cost * 0.06  # 6% consumables
    subtotal = material_cost + labor_cost + consumables
    markup = subtotal * 0.35  # 35% markup
    total = subtotal + markup
    margin = (markup / total * 100) if total > 0 else 0
    
    return {
        "material_cost": material_cost,
        "labor_cost": labor_cost,
        "consumables": consumables,
        "subtotal": subtotal,
        "markup": markup,
        "total": total,
        "margin": margin
    }