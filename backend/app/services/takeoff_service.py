
from __future__ import annotations

from typing import Dict, Any, List, Optional
from decimal import Decimal

# ======= Constants from your spreadsheet =======
# Labor operations - some are per-foot, others are per-piece
LABOR_OPERATIONS_CONFIG = {
    "Pressbrake Forming": {"rate": Decimal("0.5"), "type": "per_ft"},
    "Roll Forming": {"rate": Decimal("0.5"), "type": "per_ft"},
    "Saw Cutting": {"rate": Decimal("0.18"), "type": "per_ft"},
    "Drill & Punch": {"rate": Decimal("0.24"), "type": "per_ft"},
    "Dragon Plasma Cutting": {"rate": Decimal("0.18"), "type": "per_ft"},
    "Beam Line Cutting": {"rate": Decimal("1.0"), "type": "per_piece"},  # 1 hour per piece
    "Shearing": {"rate": Decimal("0.0667"), "type": "per_ft"},
}

# Backwards compatibility - keep the old constant for any legacy code
LABOR_OPERATIONS_HR_PER_FT = {k: v["rate"] for k, v in LABOR_OPERATIONS_CONFIG.items()}
LABOR_RATE_PER_HOUR = Decimal("120")  # Constants -> Labor Rate
MARKUP = Decimal("0.35")              # Constants -> Markup
HANDLING = Decimal("0.2")             # Constants -> Handling

COATING_SYSTEMS = {
    # area-based ($/SQFT)
    "Shop Coating": {"type": "area", "rate": Decimal("2.85")},
    "Epoxy": {"type": "area", "rate": Decimal("4.85")},
    "Powder Coat": {"type": "area", "rate": Decimal("4.85")},
    # weight-based ($/LB)
    "Galvanized": {"type": "weight", "rate": Decimal("0.67")},
    # none
    "None": {"type": "none", "rate": Decimal("0")},
}

class TakeoffCalculationService:
    """
    Service that performs material, labor, and coating calculations.
    This version adds checkbox-driven labor operations and coating selections.
    """

    # -------------------------------
    # Material Calculations
    # -------------------------------
    def calculate_entry(
        self,
        qty: int,
        shape_key: str,
        length_ft: float,
        width_ft: float = 0.0,
        material_data: Optional[Any] = None,
        unit_price_per_cwt: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Basic material calc. This is a placeholder that assumes:
        - weight_per_ft is available from material_data (Decimal or float)
        - unit_price_per_cwt is provided or taken from material_data
        Modify as needed to match your desktop logic.
        """
        # Pull properties
        if material_data is not None:
            weight_per_ft = Decimal(str(getattr(material_data, "weight_per_ft", 0) or 0))
            unit_price = Decimal(str(unit_price_per_cwt if unit_price_per_cwt is not None else getattr(material_data, "unit_price_per_cwt", 0) or 0))
            description = getattr(material_data, "description", shape_key)
            category = getattr(material_data, "category", "Other")
        else:
            # Fallback demo values
            weight_per_ft = Decimal("10.0")
            unit_price = Decimal(str(unit_price_per_cwt or "50.0"))
            description = shape_key
            category = "Other"

        total_length_ft = Decimal(str(qty)) * Decimal(str(length_ft))
        total_weight_lbs = total_length_ft * weight_per_ft
        total_weight_tons = total_weight_lbs / Decimal("2000")

        # Convert CWT to price: CWT = 100 lb
        material_cost = (total_weight_lbs / Decimal("100")) * unit_price

        return {
            "qty": qty,
            "shape_key": shape_key.upper(),
            "description": description,
            "length_ft": Decimal(str(length_ft)),
            "width_ft": Decimal(str(width_ft or 0)),
            "weight_per_ft": weight_per_ft,
            "unit_price_per_cwt": unit_price,
            "category": category,
            "total_length_ft": total_length_ft,
            "total_weight_lbs": total_weight_lbs,
            "total_weight_tons": total_weight_tons,
            "total_price": material_cost,
        }

    # -------------------------------
    # Labor Calculations
    # -------------------------------
    def calculate_labor_hours(
        self,
        material_key: str,
        qty: int,
        length_ft: float,
        width_ft: float = 0.0,
        mode: str = "auto",
        operations: Optional[List[str]] = None,
        labor_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate labor hours and cost.
        - If operations provided (checkboxes), sum hours for each selected op.
        - Otherwise, fall back to heuristic by shape (auto mode).
        Hours model assumed: hr/ft * length_ft * qty for cutting/forming operations.
        """
        length_ft_dec = Decimal(str(length_ft))
        qty_dec = Decimal(str(qty))
        total_hours = Decimal("0")
        
        if operations:
            for op in operations:
                # Handle both string and enum operations
                op_name = op.value if hasattr(op, 'value') else str(op)
                
                if op_name not in LABOR_OPERATIONS_CONFIG:
                    continue
                    
                config = LABOR_OPERATIONS_CONFIG[op_name]
                rate = config["rate"]
                calc_type = config["type"]
                
                if calc_type == "per_piece":
                    # For per-piece operations (like Beam Line): QTY × rate
                    total_hours += qty_dec * rate
                else:
                    # For per-foot operations: QTY × LENGTH × rate
                    total_hours += qty_dec * length_ft_dec * rate
        else:
            # Auto heuristic if no checkboxes selected
            key = (material_key or "").upper()
            if key.startswith("PL"):
                op = "Shearing"
            elif key.startswith("W"):
                op = "Beam Line Cutting"
            else:
                op = "Saw Cutting"
                
            config = LABOR_OPERATIONS_CONFIG.get(op, {"rate": Decimal("0"), "type": "per_ft"})
            rate = config["rate"]
            calc_type = config["type"]
            
            if calc_type == "per_piece":
                # For per-piece operations: QTY × rate
                total_hours = qty_dec * rate
            else:
                # For per-foot operations: QTY × LENGTH × rate
                total_hours = qty_dec * length_ft_dec * rate

        # Apply custom labor type multiplier if specified
        custom_multiplier = Decimal("1.0")
        total_multiplier = Decimal("1.0")
        
        if labor_type:
            labor_types = self.get_available_labor_types()
            if labor_type in labor_types:
                custom_multiplier = Decimal(str(labor_types[labor_type]["multiplier"]))
                total_multiplier = custom_multiplier
        
        # Apply multipliers to hours and cost
        final_hours = total_hours * total_multiplier
        labor_cost = final_hours * LABOR_RATE_PER_HOUR
        
        return {
            "labor_hours": float(final_hours),
            "labor_rate": float(LABOR_RATE_PER_HOUR),
            "labor_cost": float(labor_cost),
            "mode": mode or "auto",
            "custom_multiplier": float(custom_multiplier),
            "total_multiplier": float(total_multiplier),
            "base_hours": float(total_hours),
            "labor_type": labor_type,
        }

    # -------------------------------
    # Coating Calculations
    # -------------------------------
    def calculate_coatings(
        self,
        material_key: str,
        qty: int,
        length_ft: float,
        width_ft: float,
        total_weight_lbs: Optional[Decimal] = None,
        coatings_selected: Optional[List[str]] = None,
        primary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate coating cost for selected coating systems.
        Priority: coatings_selected (checkbox array) -> primary only.
        - Area-based systems priced using a simple sqft proxy.
        - Weight-based systems (Galvanized) priced per lb.
        """
        applied: Dict[str, Dict[str, Any]] = {}
        total_cost = Decimal("0")
        details: Dict[str, Any] = {}

        # Determine selection list - only primary coating, no secondary
        selection: List[str] = []
        if coatings_selected:
            selection = [c for c in coatings_selected if c in COATING_SYSTEMS]
        else:
            if primary and primary in COATING_SYSTEMS:
                selection.append(primary)

        qty_dec = Decimal(str(qty))
        length_ft_dec = Decimal(str(length_ft))
        width_ft_dec = Decimal(str(width_ft or 0))

        # Simplified surface area proxy
        # If width provided (plate), sqft ≈ qty * length_ft * width_ft
        # Else assume 1 sqft per ft as a conservative proxy.
        if width_ft_dec > 0:
            sqft_proxy = qty_dec * length_ft_dec * width_ft_dec
        else:
            sqft_proxy = qty_dec * length_ft_dec  # 1 sqft/ft

        weight_lbs = total_weight_lbs or Decimal("0")

        for coat in selection:
            system = COATING_SYSTEMS.get(coat, {"type": "none", "rate": Decimal("0")})
            if system["type"] == "area":
                cost = sqft_proxy * system["rate"]
                applied[coat] = {"type": "area", "sqft": sqft_proxy, "rate": system["rate"], "cost": cost}
                total_cost += cost
            elif system["type"] == "weight":
                cost = weight_lbs * system["rate"]
                applied[coat] = {"type": "weight", "lbs": weight_lbs, "rate": system["rate"], "cost": cost}
                total_cost += cost
            else:
                applied[coat] = {"type": "none", "cost": Decimal("0")}

        return {
            "coatings": applied or None,
            "coating_cost": total_cost if total_cost > 0 else None,
            "coating_details": details or None,
        }

    # -------------------------------
    # Totals
    # -------------------------------
    def calculate_project_totals(self, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sum up materials, labor, coatings, apply handling & markup.
        Expected per-entry keys:
          total_price, labor_cost, coating_cost
        """
        total_entries = len(entries)
        total_length_ft = sum(Decimal(str(e.get("total_length_ft", 0) or 0)) for e in entries)
        total_weight_lbs = sum(Decimal(str(e.get("total_weight_lbs", 0) or 0)) for e in entries)
        total_weight_tons = sum(Decimal(str(e.get("total_weight_tons", 0) or 0)) for e in entries)

        total_material_cost = sum(Decimal(str(e.get("total_price", 0) or 0)) for e in entries)
        total_labor_cost = sum(Decimal(str(e.get("labor_cost", 0) or 0)) for e in entries)
        total_coating_cost = sum(Decimal(str(e.get("coating_cost", 0) or 0)) for e in entries)

        # Handling on material only (common), then markup on subtotal. Adjust if your policy differs.
        handling_cost = total_material_cost * HANDLING
        subtotal = total_material_cost + handling_cost + total_labor_cost + total_coating_cost
        markup_cost = subtotal * MARKUP
        total_project_cost = subtotal + markup_cost

        return {
            "total_entries": total_entries,
            "total_length_ft": total_length_ft,
            "total_weight_lbs": total_weight_lbs,
            "total_weight_tons": total_weight_tons,
            "total_material_cost": total_material_cost,
            "total_labor_hours": sum(Decimal(str(e.get("labor_hours", 0) or 0)) for e in entries),
            "total_labor_cost": total_labor_cost,
            "total_coating_cost": total_coating_cost,
            "total_project_cost": total_project_cost,
            "by_category": {},  # fill externally if needed
        }

    # Optional helper to surface coating catalog
    def get_available_coatings(self) -> List[Dict[str, Any]]:
        out = []
        for k, v in COATING_SYSTEMS.items():
            out.append({"name": k, "type": v["type"], "rate": str(v["rate"])})
        return out

    def get_available_labor_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available labor types with multipliers and descriptions
        Returns labor types like Stairs (1.25x), Handrail (1.25x), etc.
        """
        return {
            "stairs": {
                "name": "Stairs",
                "multiplier": 1.25,
                "description": "Stair fabrication with 25% complexity increase"
            },
            "handrail": {
                "name": "Handrail",
                "multiplier": 1.25,
                "description": "Handrail installation with 25% complexity increase"
            },
            "welding_complex": {
                "name": "Complex Welding",
                "multiplier": 1.5,
                "description": "Complex welding operations with 50% time increase"
            },
            "field_work": {
                "name": "Field Work",
                "multiplier": 1.35,
                "description": "Field installation with 35% complexity increase"
            },
            "confined_space": {
                "name": "Confined Space",
                "multiplier": 1.4,
                "description": "Confined space work with 40% safety overhead"
            }
        }
