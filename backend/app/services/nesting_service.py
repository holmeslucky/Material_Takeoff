"""
Capitol Engineering Company - Material Nesting & Optimization Service
Simple, proven nesting algorithm based on working VBS macro
"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from dataclasses import dataclass
import math

@dataclass
class MaterialPurchase:
    shape_key: str
    size_description: str
    pieces_needed: int
    total_cost: float
    waste_percentage: float
    waste_cost: float = 0.0
    stock_length: float = 0.0
    cuts_per_stick: List[float] = None
    cuts_from_this_size: List[float] = None
    
    def __post_init__(self):
        if self.cuts_per_stick is None:
            self.cuts_per_stick = []
        if self.cuts_from_this_size is None:
            self.cuts_from_this_size = []

@dataclass 
class NestingResult:
    material_purchases: List[MaterialPurchase]
    total_waste_percentage: float
    total_cost: float
    cost_savings: float
    optimization_summary: str

class NestingService:
    def __init__(self):
        # Standard stock lengths in inches (from VBS: 720, 600, 480, 360, 240, 120)
        self.standard_stock_lengths = [720, 600, 480, 360, 240, 120]  # 60', 50', 40', 30', 20', 10'
        
        # Standard plate sizes (width x length in inches)
        self.standard_plate_sizes = [
            (48, 96), (48, 120), (60, 120), (60, 96), (48, 144), 
            (60, 144), (96, 96), (96, 240), (120, 480), (96, 480), (72, 144)
        ]

    def optimize_project_materials(self, takeoff_entries: List[Dict[str, Any]], project_id: str) -> NestingResult:
        """Main optimization function using the proven VBS algorithm"""
        try:
            print(f"Starting nesting optimization for project {project_id}")
            
            # Separate linear materials from plates
            linear_materials = {}
            plate_materials = {}
            
            for entry in takeoff_entries:
                shape_key = entry.get('shape_key', '').upper().strip()
                if not shape_key:
                    continue
                    
                qty = int(entry.get('qty', 0))
                if qty <= 0:
                    continue
                
                # Check if it's a plate (starts with PL or has DUCT)
                if shape_key.startswith('PL') or 'DUCT' in shape_key:
                    self._process_plate_entry(entry, plate_materials)
                else:
                    self._process_linear_entry(entry, linear_materials)
            
            # Process linear materials
            linear_purchases = []
            for material, cuts in linear_materials.items():
                purchase = self._optimize_linear_material(material, cuts)
                if purchase:
                    linear_purchases.append(purchase)
            
            # Process plate materials  
            plate_purchases = []
            for plate_key, plate_data in plate_materials.items():
                purchase = self._optimize_plate_material(plate_key, plate_data)
                if purchase:
                    plate_purchases.append(purchase)
            
            # Combine results
            all_purchases = linear_purchases + plate_purchases
            if not all_purchases:
                return NestingResult([], 0.0, 0.0, 0.0, "No materials to optimize")
            
            # Calculate totals
            total_cost = sum(p.total_cost for p in all_purchases)
            total_waste = sum(p.waste_percentage * p.total_cost for p in all_purchases) / total_cost if total_cost > 0 else 0
            
            summary = f"Optimized {len(linear_purchases)} linear materials and {len(plate_purchases)} plate materials"
            
            return NestingResult(
                material_purchases=all_purchases,
                total_waste_percentage=total_waste,
                total_cost=total_cost,
                cost_savings=0.0,  # Calculate baseline vs optimized if needed
                optimization_summary=summary
            )
            
        except Exception as e:
            print(f"Nesting optimization error: {str(e)}")
            raise ValueError(f"Nesting optimization failed: {str(e)}")

    def _process_linear_entry(self, entry: Dict[str, Any], linear_materials: Dict[str, List[float]]):
        """Process linear material entry (beams, tubes, etc.)"""
        shape_key = entry.get('shape_key', '').upper().strip()
        qty = int(entry.get('qty', 0))
        ft = float(entry.get('length_ft', 0))
        inches = float(entry.get('length_in', 0))
        
        if qty <= 0 or (ft == 0 and inches == 0):
            return
            
        # Convert to total inches
        cut_length = (ft * 12) + inches
        
        if shape_key not in linear_materials:
            linear_materials[shape_key] = []
            
        # Add each piece individually
        for _ in range(qty):
            linear_materials[shape_key].append(cut_length)

    def _process_plate_entry(self, entry: Dict[str, Any], plate_materials: Dict[str, Dict]):
        """Process plate material entry"""
        shape_key = entry.get('shape_key', '').upper().strip()
        qty = int(entry.get('qty', 0))
        width = float(entry.get('width_in', 0))
        ft = float(entry.get('length_ft', 0))
        inches = float(entry.get('length_in', 0))
        
        if qty <= 0 or width == 0:
            return
            
        length = (ft * 12) + inches
        if length == 0:
            return
            
        # Create unique key for each plate size
        plate_key = f"{shape_key}|{width}|{length}"
        
        if plate_key in plate_materials:
            plate_materials[plate_key]['qty'] += qty
        else:
            plate_materials[plate_key] = {
                'material': shape_key,
                'width': width,
                'length': length,
                'qty': qty
            }

    def _optimize_linear_material(self, material: str, cuts: List[float]) -> Optional[MaterialPurchase]:
        """Optimize linear material using greedy bin packing (from VBS macro)"""
        if not cuts:
            return None
            
        # Sort cuts by length, largest first (greedy approach)
        sorted_cuts = sorted(cuts, reverse=True)
        
        # Use largest standard stock length (720" = 60')
        stock_length = self.standard_stock_lengths[0]  # 720"
        
        # Bin packing algorithm
        sticks = []  # Each stick tracks remaining space
        stick_cuts = []  # Track what cuts are on each stick
        
        for cut_length in sorted_cuts:
            placed = False
            
            # Try to place in existing stick
            for i, remaining_space in enumerate(sticks):
                if remaining_space >= cut_length:
                    sticks[i] -= cut_length
                    stick_cuts[i].append(cut_length)
                    placed = True
                    break
            
            # If can't fit in existing stick, start new one
            if not placed:
                sticks.append(stock_length - cut_length)
                stick_cuts.append([cut_length])
        
        # Calculate metrics
        num_sticks = len(sticks)
        total_used = sum(sum(cuts_on_stick) for cuts_on_stick in stick_cuts)
        total_available = num_sticks * stock_length
        total_waste = total_available - total_used
        
        efficiency = (total_used / total_available) * 100 if total_available > 0 else 0
        waste_percentage = (total_waste / total_available) * 100 if total_available > 0 else 0
        
        # Estimate cost (placeholder - could be enhanced with real pricing)
        cost_per_stick = 100.0  # $100 per stick placeholder
        total_cost = num_sticks * cost_per_stick
        waste_cost = (total_waste / stock_length) * cost_per_stick if stock_length > 0 else 0
        
        # Flatten all cuts for cuts_from_this_size
        all_cuts = []
        for cuts_on_stick in stick_cuts:
            all_cuts.extend(cuts_on_stick)
        
        return MaterialPurchase(
            shape_key=material,
            size_description=f"{stock_length/12:.0f}' sticks",
            pieces_needed=num_sticks,
            total_cost=total_cost,
            waste_percentage=waste_percentage,
            waste_cost=waste_cost,
            stock_length=stock_length,
            cuts_per_stick=stick_cuts,
            cuts_from_this_size=all_cuts
        )

    def _optimize_plate_material(self, plate_key: str, plate_data: Dict) -> Optional[MaterialPurchase]:
        """Optimize plate material by finding best fitting standard sheet"""
        material = plate_data['material']
        width = plate_data['width']
        length = plate_data['length']
        qty = plate_data['qty']
        
        # Calculate area of single piece
        piece_area = width * length  # square inches
        
        # Find best fitting stock sheet
        best_fit = None
        best_waste = float('inf')
        
        for stock_width, stock_length in self.standard_plate_sizes:
            stock_area = stock_width * stock_length
            
            # Check if piece fits
            if (width <= stock_width and length <= stock_length) or \
               (width <= stock_length and length <= stock_width):
                waste = stock_area - piece_area
                if waste < best_waste:
                    best_waste = waste
                    best_fit = (stock_width, stock_length)
        
        if not best_fit:
            best_fit = (96, 240)  # Default to largest sheet
            best_waste = (96 * 240) - piece_area
        
        # Calculate metrics
        stock_area = best_fit[0] * best_fit[1]
        waste_percentage = (best_waste / stock_area) * 100
        
        # Calculate both-sides square footage (from VBS macro)
        total_sqft_both_sides = (piece_area / 144) * 2 * qty
        
        # Estimate cost
        cost_per_sqft = 5.0  # $5 per sqft placeholder
        total_cost = total_sqft_both_sides * cost_per_sqft
        waste_cost = (best_waste / stock_area) * total_cost if stock_area > 0 else 0
        
        return MaterialPurchase(
            shape_key=material,
            size_description=f"{best_fit[0]}x{best_fit[1]} sheets",
            pieces_needed=qty,
            total_cost=total_cost,
            waste_percentage=waste_percentage,
            waste_cost=waste_cost,
            cuts_from_this_size=[piece_area] * qty  # Each piece is one "cut"
        )

# Create global instance for import
nesting_service = NestingService()