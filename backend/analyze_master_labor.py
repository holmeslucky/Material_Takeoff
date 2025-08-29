"""
Analyze labor rates from MASTER TAKEOFF file
"""

import pandas as pd
import numpy as np

def analyze_labor_rates():
    master_file = r"C:\Users\holme\OneDrive\Desktop\Spreadsheet CE\MASTER TAKEOFF (IMPORTANT)7.13.25.xlsm"
    
    print("=== LABOR RATES ANALYSIS ===")
    
    # Read Labor Rates sheet
    df = pd.read_excel(master_file, sheet_name='Labor Rates')
    print("Complete Labor Rates sheet:")
    print(df)
    
    print("\n=== KEY RATES ===")
    labor_rate = df[df["Operation"] == "Labor Rate"]["Rate/hr"].iloc[0]
    markup = df[df["Operation"] == "Markup"]["Rate/hr"].iloc[0]
    handling = df[df["Operation"] == "Handling"]["Rate/hr"].iloc[0]
    
    print(f"Labor Rate: ${labor_rate}/hr")
    print(f"Markup: {markup*100}%")
    print(f"Handling: {handling*100}%")
    
    # Search Labor Page for stair/handrail specific data
    print("\n=== SEARCHING LABOR PAGE FOR STAIRS/HANDRAIL ===")
    df2 = pd.read_excel(master_file, sheet_name='Labor Page', header=None)
    
    # Search for stair/handrail keywords in all cells
    found_stairs = []
    found_handrail = []
    
    for i, row in df2.iterrows():
        for j, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, str):
                cell_lower = cell.lower()
                if 'stair' in cell_lower:
                    found_stairs.append((i, j, cell))
                if 'handrail' in cell_lower or 'hand rail' in cell_lower:
                    found_handrail.append((i, j, cell))
    
    print(f"Found {len(found_stairs)} stair references:")
    for item in found_stairs:
        print(f"  Row {item[0]}, Col {item[1]}: {item[2]}")
    
    print(f"Found {len(found_handrail)} handrail references:")  
    for item in found_handrail:
        print(f"  Row {item[0]}, Col {item[1]}: {item[2]}")
    
    # Look around found references for rates
    if found_stairs or found_handrail:
        print("\n=== CONTEXT AROUND FOUND REFERENCES ===")
        for refs, name in [(found_stairs, 'STAIRS'), (found_handrail, 'HANDRAIL')]:
            for ref in refs[:3]:  # Only check first 3 matches
                row, col = ref[0], ref[1]
                print(f"\n{name} context around row {row}, col {col}:")
                # Show surrounding cells
                start_row = max(0, row-2)
                end_row = min(df2.shape[0], row+3)
                start_col = max(0, col-2)
                end_col = min(df2.shape[1], col+3)
                
                context = df2.iloc[start_row:end_row, start_col:end_col]
                print(context)
    
    # Also search for numeric values that might be rates
    print("\n=== SEARCHING FOR RATE-LIKE VALUES ===")
    for i, row in df2.iterrows():
        for j, cell in enumerate(row):
            if pd.notna(cell) and isinstance(cell, (int, float)):
                if 0.5 <= cell <= 2.0:  # Look for multiplier-like values
                    # Check surrounding context
                    context_cells = []
                    for r in range(max(0, i-1), min(df2.shape[0], i+2)):
                        for c in range(max(0, j-2), min(df2.shape[1], j+3)):
                            if pd.notna(df2.iloc[r, c]):
                                context_cells.append(str(df2.iloc[r, c]))
                    
                    context_str = " ".join(context_cells).lower()
                    if any(keyword in context_str for keyword in ['stair', 'handrail', 'tread']):
                        print(f"Potential rate {cell} at row {i}, col {j} - context: {context_str[:100]}...")

if __name__ == "__main__":
    analyze_labor_rates()