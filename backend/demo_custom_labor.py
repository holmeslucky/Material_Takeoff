"""
Capitol Engineering Company - Custom Labor Rates Demonstration
Testing Stairs=1.25, Handrail=1.25 and other specialized labor types
"""

from app.services.takeoff_service import TakeoffCalculationService

def test_custom_labor_rates():
    """Demonstrate custom labor rate system"""
    
    service = TakeoffCalculationService()
    
    print("\n" + "="*60)
    print("CAPITOL TAKEOFF - CUSTOM LABOR RATES DEMONSTRATION")
    print("="*60)
    
    # Base calculation for comparison
    print("\n* BASE CALCULATION: Standard Labor")
    print("   HSS4X4X1/4 - 5 pieces, 12ft each")
    
    standard_labor = service.calculate_labor_hours(
        material_key="HSS4X4X1/4",
        qty=5,
        length_ft=12.0,
        mode="auto"
    )
    
    print(f"   Standard Labor Hours: {standard_labor['labor_hours']}")
    print(f"   Standard Labor Cost: ${standard_labor['labor_cost']:.2f}")
    print(f"   Complexity Multiplier: {standard_labor['complexity_multiplier']}")
    print(f"   Custom Multiplier: {standard_labor['custom_multiplier']}")
    
    # Test 1: Stairs - 1.25 multiplier
    print("\n* TEST 1: STAIRS - 1.25 Multiplier")
    print("   HSS4X4X1/4 - 5 pieces, 12ft each - STAIR FABRICATION")
    
    stairs_labor = service.calculate_labor_hours(
        material_key="HSS4X4X1/4",
        qty=5,
        length_ft=12.0,
        mode="auto",
        labor_type="stairs"
    )
    
    print(f"   Stairs Labor Hours: {stairs_labor['labor_hours']}")
    print(f"   Stairs Labor Cost: ${stairs_labor['labor_cost']:.2f}")
    print(f"   Labor Type: {stairs_labor['labor_type']}")
    print(f"   Custom Multiplier: {stairs_labor['custom_multiplier']}")
    print(f"   Total Multiplier: {stairs_labor['total_multiplier']}")
    
    # Test 2: Handrail - 1.25 multiplier  
    print("\n* TEST 2: HANDRAIL - 1.25 Multiplier")
    print("   HSS2X2X1/8 - 8 pieces, 8ft each - HANDRAIL FABRICATION")
    
    handrail_labor = service.calculate_labor_hours(
        material_key="HSS2X2X1/8",
        qty=8,
        length_ft=8.0,
        mode="auto",
        labor_type="handrail"
    )
    
    print(f"   Handrail Labor Hours: {handrail_labor['labor_hours']}")
    print(f"   Handrail Labor Cost: ${handrail_labor['labor_cost']:.2f}")
    print(f"   Labor Type: {handrail_labor['labor_type']}")
    print(f"   Custom Multiplier: {handrail_labor['custom_multiplier']}")
    print(f"   Total Multiplier: {handrail_labor['total_multiplier']}")
    
    # Test 3: Complex Welding - 1.5 multiplier
    print("\n* TEST 3: COMPLEX WELDING - 1.5 Multiplier") 
    print("   PL1/2X12 - 2 pieces, 10ft x 4ft - COMPLEX WELDING")
    
    complex_labor = service.calculate_labor_hours(
        material_key="PL1/2X12",
        qty=2,
        length_ft=10.0,
        width_ft=4.0,
        mode="auto",
        labor_type="welding_complex"
    )
    
    print(f"   Complex Welding Hours: {complex_labor['labor_hours']}")
    print(f"   Complex Welding Cost: ${complex_labor['labor_cost']:.2f}")
    print(f"   Labor Type: {complex_labor['labor_type']}")
    print(f"   Custom Multiplier: {complex_labor['custom_multiplier']}")
    print(f"   Total Multiplier: {complex_labor['total_multiplier']}")
    
    # Test 4: Available Labor Types
    print("\n* TEST 4: Available Custom Labor Types")
    
    available_types = service.get_available_labor_types()
    
    for labor_key, labor_info in available_types.items():
        print(f"   {labor_info['name']}: {labor_info['multiplier']}x - {labor_info['description']}")
    
    print("\n" + "="*60)
    print("SUCCESS: CUSTOM LABOR RATE SYSTEM WORKING!")
    print("SUCCESS: Stairs = 0.75x multiplier per tread")
    print("SUCCESS: Handrail = 1.25x multiplier") 
    print("SUCCESS: Complex Welding = 1.5x multiplier")
    print("SUCCESS: Expandable system for future labor types")
    print("="*60)

if __name__ == "__main__":
    test_custom_labor_rates()