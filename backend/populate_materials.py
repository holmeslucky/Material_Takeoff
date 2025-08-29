#!/usr/bin/env python3
"""
Capitol Engineering Company - Material Database Population
Populate comprehensive steel material database with standard shapes
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.material import Material
from app.core.database import Base, DATABASE_URL

def populate_wide_flange_beams():
    """Populate standard W-shape (wide flange) beams"""
    wide_flange_data = [
        # W4 Series
        {"shape_key": "W4X13", "weight_per_ft": 13.0, "depth_inches": 4.16, "width_inches": 4.06, "commonly_used": True},
        
        # W6 Series  
        {"shape_key": "W6X9", "weight_per_ft": 9.0, "depth_inches": 5.9, "width_inches": 3.94, "commonly_used": False},
        {"shape_key": "W6X12", "weight_per_ft": 12.0, "depth_inches": 6.03, "width_inches": 4.0, "commonly_used": True},
        {"shape_key": "W6X15", "weight_per_ft": 15.0, "depth_inches": 5.99, "width_inches": 5.99, "commonly_used": True},
        {"shape_key": "W6X20", "weight_per_ft": 20.0, "depth_inches": 6.2, "width_inches": 6.02, "commonly_used": True},
        {"shape_key": "W6X25", "weight_per_ft": 25.0, "depth_inches": 6.38, "width_inches": 6.08, "commonly_used": True},
        
        # W8 Series
        {"shape_key": "W8X10", "weight_per_ft": 10.0, "depth_inches": 7.89, "width_inches": 3.94, "commonly_used": False},
        {"shape_key": "W8X13", "weight_per_ft": 13.0, "depth_inches": 7.99, "width_inches": 4.0, "commonly_used": True},
        {"shape_key": "W8X15", "weight_per_ft": 15.0, "depth_inches": 8.11, "width_inches": 4.02, "commonly_used": True},
        {"shape_key": "W8X18", "weight_per_ft": 18.0, "depth_inches": 8.14, "width_inches": 5.25, "commonly_used": True},
        {"shape_key": "W8X21", "weight_per_ft": 21.0, "depth_inches": 8.28, "width_inches": 5.27, "commonly_used": True},
        {"shape_key": "W8X24", "weight_per_ft": 24.0, "depth_inches": 7.93, "width_inches": 6.5, "commonly_used": True},
        {"shape_key": "W8X28", "weight_per_ft": 28.0, "depth_inches": 8.06, "width_inches": 6.54, "commonly_used": True},
        {"shape_key": "W8X31", "weight_per_ft": 31.0, "depth_inches": 8.0, "width_inches": 7.995, "commonly_used": True},
        {"shape_key": "W8X35", "weight_per_ft": 35.0, "depth_inches": 8.12, "width_inches": 8.02, "commonly_used": True},
        {"shape_key": "W8X40", "weight_per_ft": 40.0, "depth_inches": 8.25, "width_inches": 8.07, "commonly_used": True},
        
        # W10 Series
        {"shape_key": "W10X12", "weight_per_ft": 12.0, "depth_inches": 9.87, "width_inches": 3.96, "commonly_used": True},
        {"shape_key": "W10X15", "weight_per_ft": 15.0, "depth_inches": 9.99, "width_inches": 4.0, "commonly_used": True},
        {"shape_key": "W10X17", "weight_per_ft": 17.0, "depth_inches": 10.11, "width_inches": 4.01, "commonly_used": True},
        {"shape_key": "W10X19", "weight_per_ft": 19.0, "depth_inches": 10.24, "width_inches": 4.02, "commonly_used": True},
        {"shape_key": "W10X22", "weight_per_ft": 22.0, "depth_inches": 10.17, "width_inches": 5.75, "commonly_used": True},
        {"shape_key": "W10X26", "weight_per_ft": 26.0, "depth_inches": 10.33, "width_inches": 5.77, "commonly_used": True},
        {"shape_key": "W10X30", "weight_per_ft": 30.0, "depth_inches": 10.47, "width_inches": 5.81, "commonly_used": True},
        {"shape_key": "W10X33", "weight_per_ft": 33.0, "depth_inches": 9.73, "width_inches": 7.96, "commonly_used": True},
        {"shape_key": "W10X39", "weight_per_ft": 39.0, "depth_inches": 9.92, "width_inches": 7.99, "commonly_used": True},
        {"shape_key": "W10X45", "weight_per_ft": 45.0, "depth_inches": 10.1, "width_inches": 8.02, "commonly_used": True},
        {"shape_key": "W10X49", "weight_per_ft": 49.0, "depth_inches": 9.98, "width_inches": 10.0, "commonly_used": True},
        {"shape_key": "W10X54", "weight_per_ft": 54.0, "depth_inches": 10.09, "width_inches": 10.03, "commonly_used": True},
        
        # W12 Series - Very Common
        {"shape_key": "W12X14", "weight_per_ft": 14.0, "depth_inches": 11.91, "width_inches": 3.97, "commonly_used": True},
        {"shape_key": "W12X16", "weight_per_ft": 16.0, "depth_inches": 11.99, "width_inches": 3.99, "commonly_used": True},
        {"shape_key": "W12X19", "weight_per_ft": 19.0, "depth_inches": 12.16, "width_inches": 4.01, "commonly_used": True},
        {"shape_key": "W12X22", "weight_per_ft": 22.0, "depth_inches": 12.31, "width_inches": 4.03, "commonly_used": True},
        {"shape_key": "W12X26", "weight_per_ft": 26.0, "depth_inches": 12.22, "width_inches": 6.49, "commonly_used": True},
        {"shape_key": "W12X30", "weight_per_ft": 30.0, "depth_inches": 12.34, "width_inches": 6.52, "commonly_used": True},
        {"shape_key": "W12X35", "weight_per_ft": 35.0, "depth_inches": 12.5, "width_inches": 6.56, "commonly_used": True},
        {"shape_key": "W12X40", "weight_per_ft": 40.0, "depth_inches": 11.94, "width_inches": 8.01, "commonly_used": True},
        {"shape_key": "W12X45", "weight_per_ft": 45.0, "depth_inches": 12.06, "width_inches": 8.05, "commonly_used": True},
        {"shape_key": "W12X50", "weight_per_ft": 50.0, "depth_inches": 12.19, "width_inches": 8.08, "commonly_used": True},
        {"shape_key": "W12X53", "weight_per_ft": 53.0, "depth_inches": 12.06, "width_inches": 10.0, "commonly_used": True},
        {"shape_key": "W12X58", "weight_per_ft": 58.0, "depth_inches": 12.19, "width_inches": 10.01, "commonly_used": True},
        {"shape_key": "W12X65", "weight_per_ft": 65.0, "depth_inches": 12.12, "width_inches": 12.0, "commonly_used": True},
        {"shape_key": "W12X72", "weight_per_ft": 72.0, "depth_inches": 12.25, "width_inches": 12.04, "commonly_used": True},
        
        # W14 Series - Common for columns
        {"shape_key": "W14X22", "weight_per_ft": 22.0, "depth_inches": 13.74, "width_inches": 5.0, "commonly_used": True},
        {"shape_key": "W14X26", "weight_per_ft": 26.0, "depth_inches": 13.91, "width_inches": 5.03, "commonly_used": True},
        {"shape_key": "W14X30", "weight_per_ft": 30.0, "depth_inches": 13.84, "width_inches": 6.73, "commonly_used": True},
        {"shape_key": "W14X34", "weight_per_ft": 34.0, "depth_inches": 13.98, "width_inches": 6.75, "commonly_used": True},
        {"shape_key": "W14X38", "weight_per_ft": 38.0, "depth_inches": 14.1, "width_inches": 6.77, "commonly_used": True},
        {"shape_key": "W14X43", "weight_per_ft": 43.0, "depth_inches": 13.66, "width_inches": 7.995, "commonly_used": True},
        {"shape_key": "W14X48", "weight_per_ft": 48.0, "depth_inches": 13.79, "width_inches": 8.03, "commonly_used": True},
        {"shape_key": "W14X53", "weight_per_ft": 53.0, "depth_inches": 13.92, "width_inches": 8.06, "commonly_used": True},
        {"shape_key": "W14X61", "weight_per_ft": 61.0, "depth_inches": 13.89, "width_inches": 9.995, "commonly_used": True},
        {"shape_key": "W14X68", "weight_per_ft": 68.0, "depth_inches": 14.04, "width_inches": 10.04, "commonly_used": True},
        {"shape_key": "W14X74", "weight_per_ft": 74.0, "depth_inches": 14.17, "width_inches": 10.07, "commonly_used": True},
        {"shape_key": "W14X82", "weight_per_ft": 82.0, "depth_inches": 14.31, "width_inches": 10.13, "commonly_used": True},
        {"shape_key": "W14X90", "weight_per_ft": 90.0, "depth_inches": 14.02, "width_inches": 14.52, "commonly_used": True},
        
        # W16 Series
        {"shape_key": "W16X26", "weight_per_ft": 26.0, "depth_inches": 15.69, "width_inches": 5.5, "commonly_used": True},
        {"shape_key": "W16X31", "weight_per_ft": 31.0, "depth_inches": 15.88, "width_inches": 5.53, "commonly_used": True},
        {"shape_key": "W16X36", "weight_per_ft": 36.0, "depth_inches": 15.86, "width_inches": 6.99, "commonly_used": True},
        {"shape_key": "W16X40", "weight_per_ft": 40.0, "depth_inches": 16.01, "width_inches": 7.0, "commonly_used": True},
        {"shape_key": "W16X45", "weight_per_ft": 45.0, "depth_inches": 16.13, "width_inches": 7.04, "commonly_used": True},
        {"shape_key": "W16X50", "weight_per_ft": 50.0, "depth_inches": 16.26, "width_inches": 7.07, "commonly_used": True},
        {"shape_key": "W16X57", "weight_per_ft": 57.0, "depth_inches": 16.43, "width_inches": 7.12, "commonly_used": True},
        {"shape_key": "W16X67", "weight_per_ft": 67.0, "depth_inches": 16.33, "width_inches": 8.28, "commonly_used": True},
        {"shape_key": "W16X77", "weight_per_ft": 77.0, "depth_inches": 16.52, "width_inches": 8.29, "commonly_used": True},
        
        # W18 Series
        {"shape_key": "W18X35", "weight_per_ft": 35.0, "depth_inches": 17.7, "width_inches": 6.0, "commonly_used": True},
        {"shape_key": "W18X40", "weight_per_ft": 40.0, "depth_inches": 17.9, "width_inches": 6.02, "commonly_used": True},
        {"shape_key": "W18X46", "weight_per_ft": 46.0, "depth_inches": 18.06, "width_inches": 6.06, "commonly_used": True},
        {"shape_key": "W18X50", "weight_per_ft": 50.0, "depth_inches": 17.99, "width_inches": 7.5, "commonly_used": True},
        {"shape_key": "W18X55", "weight_per_ft": 55.0, "depth_inches": 18.11, "width_inches": 7.53, "commonly_used": True},
        {"shape_key": "W18X60", "weight_per_ft": 60.0, "depth_inches": 18.24, "width_inches": 7.56, "commonly_used": True},
        {"shape_key": "W18X65", "weight_per_ft": 65.0, "depth_inches": 18.35, "width_inches": 7.59, "commonly_used": True},
        {"shape_key": "W18X71", "weight_per_ft": 71.0, "depth_inches": 18.47, "width_inches": 7.64, "commonly_used": True},
        {"shape_key": "W18X76", "weight_per_ft": 76.0, "depth_inches": 18.21, "width_inches": 11.04, "commonly_used": True},
        {"shape_key": "W18X86", "weight_per_ft": 86.0, "depth_inches": 18.39, "width_inches": 11.09, "commonly_used": True},
        
        # W21 Series
        {"shape_key": "W21X44", "weight_per_ft": 44.0, "depth_inches": 20.66, "width_inches": 6.5, "commonly_used": True},
        {"shape_key": "W21X50", "weight_per_ft": 50.0, "depth_inches": 20.83, "width_inches": 6.53, "commonly_used": True},
        {"shape_key": "W21X57", "weight_per_ft": 57.0, "depth_inches": 21.06, "width_inches": 6.56, "commonly_used": True},
        {"shape_key": "W21X62", "weight_per_ft": 62.0, "depth_inches": 21.0, "width_inches": 8.24, "commonly_used": True},
        {"shape_key": "W21X68", "weight_per_ft": 68.0, "depth_inches": 21.13, "width_inches": 8.27, "commonly_used": True},
        {"shape_key": "W21X73", "weight_per_ft": 73.0, "depth_inches": 21.24, "width_inches": 8.3, "commonly_used": True},
        
        # W24 Series
        {"shape_key": "W24X55", "weight_per_ft": 55.0, "depth_inches": 23.57, "width_inches": 7.01, "commonly_used": True},
        {"shape_key": "W24X62", "weight_per_ft": 62.0, "depth_inches": 23.74, "width_inches": 7.04, "commonly_used": True},
        {"shape_key": "W24X68", "weight_per_ft": 68.0, "depth_inches": 23.73, "width_inches": 8.97, "commonly_used": True},
        {"shape_key": "W24X76", "weight_per_ft": 76.0, "depth_inches": 23.92, "width_inches": 8.99, "commonly_used": True},
        {"shape_key": "W24X84", "weight_per_ft": 84.0, "depth_inches": 24.1, "width_inches": 9.02, "commonly_used": True},
        {"shape_key": "W24X94", "weight_per_ft": 94.0, "depth_inches": 24.31, "width_inches": 9.07, "commonly_used": True},
        
        # W27 Series
        {"shape_key": "W27X84", "weight_per_ft": 84.0, "depth_inches": 26.71, "width_inches": 9.96, "commonly_used": True},
        {"shape_key": "W27X94", "weight_per_ft": 94.0, "depth_inches": 26.92, "width_inches": 9.99, "commonly_used": True},
        
        # W30 Series
        {"shape_key": "W30X90", "weight_per_ft": 90.0, "depth_inches": 29.53, "width_inches": 10.4, "commonly_used": True},
        {"shape_key": "W30X99", "weight_per_ft": 99.0, "depth_inches": 29.65, "width_inches": 10.45, "commonly_used": True},
        {"shape_key": "W30X108", "weight_per_ft": 108.0, "depth_inches": 29.83, "width_inches": 10.48, "commonly_used": True},
    ]
    
    materials = []
    for data in wide_flange_data:
        material = Material(
            shape_key=data["shape_key"],
            description=f"Wide Flange Beam {data['shape_key']} - {data['weight_per_ft']} lb/ft",
            category="Wide Flange",
            material_type="Steel",
            grade="A992",
            weight_per_ft=data["weight_per_ft"],
            depth_inches=data["depth_inches"],
            width_inches=data["width_inches"],
            unit_price_per_cwt=85.00,  # Default steel price per CWT
            supplier="Capitol Steel",
            commonly_used=data["commonly_used"]
        )
        materials.append(material)
    
    return materials

def populate_plate_materials():
    """Populate standard plate materials"""
    plate_data = [
        # Common plate thicknesses
        {"shape_key": "PL1/4", "thickness": 0.25, "commonly_used": True},
        {"shape_key": "PL5/16", "thickness": 0.3125, "commonly_used": True},
        {"shape_key": "PL3/8", "thickness": 0.375, "commonly_used": True},
        {"shape_key": "PL1/2", "thickness": 0.5, "commonly_used": True},
        {"shape_key": "PL5/8", "thickness": 0.625, "commonly_used": True},
        {"shape_key": "PL3/4", "thickness": 0.75, "commonly_used": True},
        {"shape_key": "PL7/8", "thickness": 0.875, "commonly_used": False},
        {"shape_key": "PL1", "thickness": 1.0, "commonly_used": True},
        {"shape_key": "PL1-1/4", "thickness": 1.25, "commonly_used": False},
        {"shape_key": "PL1-1/2", "thickness": 1.5, "commonly_used": False},
        {"shape_key": "PL2", "thickness": 2.0, "commonly_used": False},
        
        # Specific sized plates
        {"shape_key": "PL1/2X12", "thickness": 0.5, "width_inches": 12.0, "commonly_used": True},
        {"shape_key": "PL3/4X12", "thickness": 0.75, "width_inches": 12.0, "commonly_used": True},
        {"shape_key": "PL1X12", "thickness": 1.0, "width_inches": 12.0, "commonly_used": True},
        {"shape_key": "PL1/2X6", "thickness": 0.5, "width_inches": 6.0, "commonly_used": True},
        {"shape_key": "PL3/8X6", "thickness": 0.375, "width_inches": 6.0, "commonly_used": True},
    ]
    
    materials = []
    for data in plate_data:
        # Calculate weight per square foot for plates
        steel_density = 40.8  # lbs per cubic foot
        weight_per_sq_ft = (data["thickness"] / 12.0) * steel_density
        
        material = Material(
            shape_key=data["shape_key"],
            description=f"Steel Plate {data['thickness']}\" thick - {weight_per_sq_ft:.1f} lb/sq ft",
            category="Plate", 
            material_type="Steel",
            grade="A36",
            weight_per_ft=weight_per_sq_ft,  # For plates, this is weight per sq ft
            thickness_inches=data["thickness"],
            width_inches=data.get("width_inches"),
            unit_price_per_cwt=88.00,  # Plate typically costs more
            supplier="Capitol Steel",
            commonly_used=data["commonly_used"]
        )
        materials.append(material)
    
    return materials

def populate_angle_materials():
    """Populate standard angle materials"""
    angle_data = [
        # Equal leg angles
        {"shape_key": "L2X2X1/4", "leg1": 2.0, "leg2": 2.0, "thickness": 0.25, "weight_per_ft": 1.19, "commonly_used": True},
        {"shape_key": "L2X2X5/16", "leg1": 2.0, "leg2": 2.0, "thickness": 0.3125, "weight_per_ft": 1.44, "commonly_used": True},
        {"shape_key": "L2X2X3/8", "leg1": 2.0, "leg2": 2.0, "thickness": 0.375, "weight_per_ft": 1.65, "commonly_used": True},
        {"shape_key": "L3X3X1/4", "leg1": 3.0, "leg2": 3.0, "thickness": 0.25, "weight_per_ft": 1.85, "commonly_used": True},
        {"shape_key": "L3X3X5/16", "leg1": 3.0, "leg2": 3.0, "thickness": 0.3125, "weight_per_ft": 2.30, "commonly_used": True},
        {"shape_key": "L3X3X3/8", "leg1": 3.0, "leg2": 3.0, "thickness": 0.375, "weight_per_ft": 2.75, "commonly_used": True},
        {"shape_key": "L3X3X1/2", "leg1": 3.0, "leg2": 3.0, "thickness": 0.5, "weight_per_ft": 3.58, "commonly_used": True},
        {"shape_key": "L4X4X1/4", "leg1": 4.0, "leg2": 4.0, "thickness": 0.25, "weight_per_ft": 2.44, "commonly_used": True},
        {"shape_key": "L4X4X5/16", "leg1": 4.0, "leg2": 4.0, "thickness": 0.3125, "weight_per_ft": 3.05, "commonly_used": True},
        {"shape_key": "L4X4X3/8", "leg1": 4.0, "leg2": 4.0, "thickness": 0.375, "weight_per_ft": 3.64, "commonly_used": True},
        {"shape_key": "L4X4X1/2", "leg1": 4.0, "leg2": 4.0, "thickness": 0.5, "weight_per_ft": 4.75, "commonly_used": True},
        {"shape_key": "L5X5X5/16", "leg1": 5.0, "leg2": 5.0, "thickness": 0.3125, "weight_per_ft": 3.86, "commonly_used": True},
        {"shape_key": "L5X5X3/8", "leg1": 5.0, "leg2": 5.0, "thickness": 0.375, "weight_per_ft": 4.61, "commonly_used": True},
        {"shape_key": "L5X5X1/2", "leg1": 5.0, "leg2": 5.0, "thickness": 0.5, "weight_per_ft": 6.04, "commonly_used": True},
        {"shape_key": "L6X6X3/8", "leg1": 6.0, "leg2": 6.0, "thickness": 0.375, "weight_per_ft": 5.57, "commonly_used": True},
        {"shape_key": "L6X6X1/2", "leg1": 6.0, "leg2": 6.0, "thickness": 0.5, "weight_per_ft": 7.32, "commonly_used": True},
        {"shape_key": "L6X6X5/8", "leg1": 6.0, "leg2": 6.0, "thickness": 0.625, "weight_per_ft": 9.02, "commonly_used": True},
        {"shape_key": "L8X8X1/2", "leg1": 8.0, "leg2": 8.0, "thickness": 0.5, "weight_per_ft": 9.79, "commonly_used": True},
        {"shape_key": "L8X8X5/8", "leg1": 8.0, "leg2": 8.0, "thickness": 0.625, "weight_per_ft": 12.17, "commonly_used": True},
        
        # Unequal leg angles
        {"shape_key": "L3X2X1/4", "leg1": 3.0, "leg2": 2.0, "thickness": 0.25, "weight_per_ft": 1.30, "commonly_used": True},
        {"shape_key": "L3X2X5/16", "leg1": 3.0, "leg2": 2.0, "thickness": 0.3125, "weight_per_ft": 1.59, "commonly_used": True},
        {"shape_key": "L4X3X1/4", "leg1": 4.0, "leg2": 3.0, "thickness": 0.25, "weight_per_ft": 1.74, "commonly_used": True},
        {"shape_key": "L4X3X5/16", "leg1": 4.0, "leg2": 3.0, "thickness": 0.3125, "weight_per_ft": 2.17, "commonly_used": True},
        {"shape_key": "L4X3X3/8", "leg1": 4.0, "leg2": 3.0, "thickness": 0.375, "weight_per_ft": 2.58, "commonly_used": True},
        {"shape_key": "L5X3X1/4", "leg1": 5.0, "leg2": 3.0, "thickness": 0.25, "weight_per_ft": 2.00, "commonly_used": True},
        {"shape_key": "L5X3X5/16", "leg1": 5.0, "leg2": 3.0, "thickness": 0.3125, "weight_per_ft": 2.49, "commonly_used": True},
        {"shape_key": "L5X3X3/8", "leg1": 5.0, "leg2": 3.0, "thickness": 0.375, "weight_per_ft": 2.97, "commonly_used": True},
        {"shape_key": "L6X4X3/8", "leg1": 6.0, "leg2": 4.0, "thickness": 0.375, "weight_per_ft": 3.83, "commonly_used": True},
        {"shape_key": "L6X4X1/2", "leg1": 6.0, "leg2": 4.0, "thickness": 0.5, "weight_per_ft": 5.03, "commonly_used": True},
    ]
    
    materials = []
    for data in angle_data:
        if data["leg1"] == data["leg2"]:
            desc = f"Equal Leg Angle L{data['leg1']}X{data['leg2']}X{data['thickness']} - {data['weight_per_ft']} lb/ft"
        else:
            desc = f"Unequal Leg Angle L{data['leg1']}X{data['leg2']}X{data['thickness']} - {data['weight_per_ft']} lb/ft"
            
        material = Material(
            shape_key=data["shape_key"],
            description=desc,
            category="Angle",
            material_type="Steel", 
            grade="A36",
            weight_per_ft=data["weight_per_ft"],
            depth_inches=data["leg1"],
            width_inches=data["leg2"],
            thickness_inches=data["thickness"],
            unit_price_per_cwt=87.00,
            supplier="Capitol Steel",
            commonly_used=data["commonly_used"]
        )
        materials.append(material)
    
    return materials

def populate_channel_materials():
    """Populate standard channel materials"""
    channel_data = [
        # MC Series (Miscellaneous Channels)
        {"shape_key": "MC3X7.1", "weight_per_ft": 7.1, "depth_inches": 3.0, "width_inches": 1.596, "commonly_used": True},
        {"shape_key": "MC4X13.8", "weight_per_ft": 13.8, "depth_inches": 4.0, "width_inches": 2.072, "commonly_used": True},
        {"shape_key": "MC6X15.3", "weight_per_ft": 15.3, "depth_inches": 6.0, "width_inches": 1.84, "commonly_used": True},
        {"shape_key": "MC6X18", "weight_per_ft": 18.0, "depth_inches": 6.0, "width_inches": 1.945, "commonly_used": True},
        {"shape_key": "MC8X21.4", "weight_per_ft": 21.4, "depth_inches": 8.0, "width_inches": 2.648, "commonly_used": True},
        {"shape_key": "MC8X22.8", "weight_per_ft": 22.8, "depth_inches": 8.0, "width_inches": 2.72, "commonly_used": True},
        {"shape_key": "MC10X25", "weight_per_ft": 25.0, "depth_inches": 10.0, "width_inches": 3.032, "commonly_used": True},
        {"shape_key": "MC10X28.5", "weight_per_ft": 28.5, "depth_inches": 10.0, "width_inches": 3.115, "commonly_used": True},
        {"shape_key": "MC12X35", "weight_per_ft": 35.0, "depth_inches": 12.0, "width_inches": 3.67, "commonly_used": True},
        
        # C Series (Standard Channels)  
        {"shape_key": "C3X4.1", "weight_per_ft": 4.1, "depth_inches": 3.0, "width_inches": 1.41, "commonly_used": True},
        {"shape_key": "C3X5", "weight_per_ft": 5.0, "depth_inches": 3.0, "width_inches": 1.498, "commonly_used": True},
        {"shape_key": "C4X5.4", "weight_per_ft": 5.4, "depth_inches": 4.0, "width_inches": 1.584, "commonly_used": True},
        {"shape_key": "C4X7.25", "weight_per_ft": 7.25, "depth_inches": 4.0, "width_inches": 1.72, "commonly_used": True},
        {"shape_key": "C5X6.7", "weight_per_ft": 6.7, "depth_inches": 5.0, "width_inches": 1.75, "commonly_used": True},
        {"shape_key": "C5X9", "weight_per_ft": 9.0, "depth_inches": 5.0, "width_inches": 1.885, "commonly_used": True},
        {"shape_key": "C6X8.2", "weight_per_ft": 8.2, "depth_inches": 6.0, "width_inches": 1.92, "commonly_used": True},
        {"shape_key": "C6X10.5", "weight_per_ft": 10.5, "depth_inches": 6.0, "width_inches": 2.034, "commonly_used": True},
        {"shape_key": "C6X13", "weight_per_ft": 13.0, "depth_inches": 6.0, "width_inches": 2.157, "commonly_used": True},
        {"shape_key": "C8X11.5", "weight_per_ft": 11.5, "depth_inches": 8.0, "width_inches": 2.26, "commonly_used": True},
        {"shape_key": "C8X13.75", "weight_per_ft": 13.75, "depth_inches": 8.0, "width_inches": 2.343, "commonly_used": True},
        {"shape_key": "C8X18.75", "weight_per_ft": 18.75, "depth_inches": 8.0, "width_inches": 2.527, "commonly_used": True},
        {"shape_key": "C10X15.3", "weight_per_ft": 15.3, "depth_inches": 10.0, "width_inches": 2.6, "commonly_used": True},
        {"shape_key": "C10X20", "weight_per_ft": 20.0, "depth_inches": 10.0, "width_inches": 2.739, "commonly_used": True},
        {"shape_key": "C12X20.7", "weight_per_ft": 20.7, "depth_inches": 12.0, "width_inches": 2.942, "commonly_used": True},
        {"shape_key": "C12X25", "weight_per_ft": 25.0, "depth_inches": 12.0, "width_inches": 3.047, "commonly_used": True},
    ]
    
    materials = []
    for data in channel_data:
        material = Material(
            shape_key=data["shape_key"],
            description=f"Channel {data['shape_key']} - {data['weight_per_ft']} lb/ft",
            category="Channel",
            material_type="Steel",
            grade="A36",
            weight_per_ft=data["weight_per_ft"],
            depth_inches=data["depth_inches"],
            width_inches=data["width_inches"],
            unit_price_per_cwt=86.00,
            supplier="Capitol Steel",
            commonly_used=data["commonly_used"]
        )
        materials.append(material)
    
    return materials

def populate_hss_materials():
    """Populate HSS (Hollow Structural Section) materials"""
    hss_data = [
        # Square HSS
        {"shape_key": "HSS2X2X1/8", "depth": 2.0, "width": 2.0, "thickness": 0.125, "weight_per_ft": 1.45, "commonly_used": True},
        {"shape_key": "HSS2X2X3/16", "depth": 2.0, "width": 2.0, "thickness": 0.1875, "weight_per_ft": 2.06, "commonly_used": True},
        {"shape_key": "HSS2X2X1/4", "depth": 2.0, "width": 2.0, "thickness": 0.25, "weight_per_ft": 2.64, "commonly_used": True},
        {"shape_key": "HSS3X3X1/8", "depth": 3.0, "width": 3.0, "thickness": 0.125, "weight_per_ft": 2.29, "commonly_used": True},
        {"shape_key": "HSS3X3X3/16", "depth": 3.0, "width": 3.0, "thickness": 0.1875, "weight_per_ft": 3.31, "commonly_used": True},
        {"shape_key": "HSS3X3X1/4", "depth": 3.0, "width": 3.0, "thickness": 0.25, "weight_per_ft": 4.29, "commonly_used": True},
        {"shape_key": "HSS4X4X1/8", "depth": 4.0, "width": 4.0, "thickness": 0.125, "weight_per_ft": 3.14, "commonly_used": True},
        {"shape_key": "HSS4X4X3/16", "depth": 4.0, "width": 4.0, "thickness": 0.1875, "weight_per_ft": 4.57, "commonly_used": True},
        {"shape_key": "HSS4X4X1/4", "depth": 4.0, "width": 4.0, "thickness": 0.25, "weight_per_ft": 5.95, "commonly_used": True},
        {"shape_key": "HSS4X4X5/16", "depth": 4.0, "width": 4.0, "thickness": 0.3125, "weight_per_ft": 7.27, "commonly_used": True},
        {"shape_key": "HSS5X5X1/4", "depth": 5.0, "width": 5.0, "thickness": 0.25, "weight_per_ft": 7.6, "commonly_used": True},
        {"shape_key": "HSS5X5X5/16", "depth": 5.0, "width": 5.0, "thickness": 0.3125, "weight_per_ft": 9.32, "commonly_used": True},
        {"shape_key": "HSS6X6X1/4", "depth": 6.0, "width": 6.0, "thickness": 0.25, "weight_per_ft": 9.25, "commonly_used": True},
        {"shape_key": "HSS6X6X5/16", "depth": 6.0, "width": 6.0, "thickness": 0.3125, "weight_per_ft": 11.37, "commonly_used": True},
        {"shape_key": "HSS6X6X3/8", "depth": 6.0, "width": 6.0, "thickness": 0.375, "weight_per_ft": 13.44, "commonly_used": True},
        {"shape_key": "HSS8X8X1/4", "depth": 8.0, "width": 8.0, "thickness": 0.25, "weight_per_ft": 12.54, "commonly_used": True},
        {"shape_key": "HSS8X8X5/16", "depth": 8.0, "width": 8.0, "thickness": 0.3125, "weight_per_ft": 15.47, "commonly_used": True},
        {"shape_key": "HSS8X8X3/8", "depth": 8.0, "width": 8.0, "thickness": 0.375, "weight_per_ft": 18.33, "commonly_used": True},
        
        # Rectangular HSS
        {"shape_key": "HSS3X2X3/16", "depth": 3.0, "width": 2.0, "thickness": 0.1875, "weight_per_ft": 2.69, "commonly_used": True},
        {"shape_key": "HSS3X2X1/4", "depth": 3.0, "width": 2.0, "thickness": 0.25, "weight_per_ft": 3.47, "commonly_used": True},
        {"shape_key": "HSS4X2X3/16", "depth": 4.0, "width": 2.0, "thickness": 0.1875, "weight_per_ft": 3.31, "commonly_used": True},
        {"shape_key": "HSS4X2X1/4", "depth": 4.0, "width": 2.0, "thickness": 0.25, "weight_per_ft": 4.29, "commonly_used": True},
        {"shape_key": "HSS4X3X3/16", "depth": 4.0, "width": 3.0, "thickness": 0.1875, "weight_per_ft": 3.94, "commonly_used": True},
        {"shape_key": "HSS4X3X1/4", "depth": 4.0, "width": 3.0, "thickness": 0.25, "weight_per_ft": 5.12, "commonly_used": True},
        {"shape_key": "HSS5X3X3/16", "depth": 5.0, "width": 3.0, "thickness": 0.1875, "weight_per_ft": 4.56, "commonly_used": True},
        {"shape_key": "HSS5X3X1/4", "depth": 5.0, "width": 3.0, "thickness": 0.25, "weight_per_ft": 5.95, "commonly_used": True},
        {"shape_key": "HSS5X3X5/16", "depth": 5.0, "width": 3.0, "thickness": 0.3125, "weight_per_ft": 7.27, "commonly_used": True},
        {"shape_key": "HSS6X4X1/4", "depth": 6.0, "width": 4.0, "thickness": 0.25, "weight_per_ft": 7.6, "commonly_used": True},
        {"shape_key": "HSS6X4X5/16", "depth": 6.0, "width": 4.0, "thickness": 0.3125, "weight_per_ft": 9.32, "commonly_used": True},
        {"shape_key": "HSS6X4X3/8", "depth": 6.0, "width": 4.0, "thickness": 0.375, "weight_per_ft": 11.01, "commonly_used": True},
        {"shape_key": "HSS8X4X1/4", "depth": 8.0, "width": 4.0, "thickness": 0.25, "weight_per_ft": 9.25, "commonly_used": True},
        {"shape_key": "HSS8X4X5/16", "depth": 8.0, "width": 4.0, "thickness": 0.3125, "weight_per_ft": 11.37, "commonly_used": True},
        {"shape_key": "HSS8X6X1/4", "depth": 8.0, "width": 6.0, "thickness": 0.25, "weight_per_ft": 10.89, "commonly_used": True},
        {"shape_key": "HSS8X6X5/16", "depth": 8.0, "width": 6.0, "thickness": 0.3125, "weight_per_ft": 13.42, "commonly_used": True},
        {"shape_key": "HSS10X6X1/4", "depth": 10.0, "width": 6.0, "thickness": 0.25, "weight_per_ft": 12.54, "commonly_used": True},
        {"shape_key": "HSS10X6X5/16", "depth": 10.0, "width": 6.0, "thickness": 0.3125, "weight_per_ft": 15.47, "commonly_used": True},
        {"shape_key": "HSS12X8X1/4", "depth": 12.0, "width": 8.0, "thickness": 0.25, "weight_per_ft": 15.82, "commonly_used": True},
        {"shape_key": "HSS12X8X5/16", "depth": 12.0, "width": 8.0, "thickness": 0.3125, "weight_per_ft": 19.57, "commonly_used": True},
    ]
    
    materials = []
    for data in hss_data:
        if data["depth"] == data["width"]:
            desc = f"Square HSS {data['shape_key']} - {data['weight_per_ft']} lb/ft"
        else:
            desc = f"Rectangular HSS {data['shape_key']} - {data['weight_per_ft']} lb/ft"
            
        material = Material(
            shape_key=data["shape_key"],
            description=desc,
            category="HSS/Tube",
            material_type="Steel",
            grade="A500",
            weight_per_ft=data["weight_per_ft"],
            depth_inches=data["depth"],
            width_inches=data["width"],
            thickness_inches=data["thickness"],
            unit_price_per_cwt=89.00,  # HSS typically costs more
            supplier="Capitol Steel",
            commonly_used=data["commonly_used"]
        )
        materials.append(material)
    
    return materials

def main():
    """Main function to populate all material categories"""
    print("Capitol Engineering Company - Material Database Population")
    print("=" * 60)
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing materials
        print("Clearing existing materials...")
        db.query(Material).delete()
        db.commit()
        
        # Populate each category
        print("Populating Wide Flange Beams...")
        wide_flange_materials = populate_wide_flange_beams()
        db.add_all(wide_flange_materials)
        db.commit()
        print(f"   Added {len(wide_flange_materials)} wide flange beams")
        
        print("Populating Plate Materials...")
        plate_materials = populate_plate_materials()
        db.add_all(plate_materials)
        db.commit()
        print(f"   Added {len(plate_materials)} plate materials")
        
        print("Populating Angle Materials...")
        angle_materials = populate_angle_materials()
        db.add_all(angle_materials)
        db.commit()
        print(f"   Added {len(angle_materials)} angle materials")
        
        print("Populating Channel Materials...")
        channel_materials = populate_channel_materials()
        db.add_all(channel_materials)
        db.commit()
        print(f"   Added {len(channel_materials)} channel materials")
        
        print("Populating HSS Materials...")
        hss_materials = populate_hss_materials()
        db.add_all(hss_materials)
        db.commit()
        print(f"   Added {len(hss_materials)} HSS materials")
        
        # Get totals
        total_materials = db.query(Material).count()
        commonly_used = db.query(Material).filter(Material.commonly_used == True).count()
        
        print("\n" + "=" * 60)
        print("MATERIAL DATABASE POPULATION COMPLETE!")
        print(f"   Total Materials: {total_materials}")
        print(f"   Commonly Used: {commonly_used}")
        print(f"   Categories: Wide Flange, Plate, Angle, Channel, HSS")
        print("=" * 60)
        
        # Show sample of commonly used materials
        print("\nSample Commonly Used Materials:")
        samples = db.query(Material).filter(Material.commonly_used == True).limit(10).all()
        for sample in samples:
            print(f"   - {sample.shape_key}: {sample.description}")
        
        print(f"\nMaterial database ready for SMART AUTOCOMPLETE!")
        print("Frontend will now show comprehensive material suggestions!")
        
    except Exception as e:
        print(f"Error populating materials: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()