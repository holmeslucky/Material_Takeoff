"""
Extract labor chart information from MASTER TAKEOFF Excel file
"""

import pandas as pd
import sys
import os

def extract_labor_info():
    """Extract labor rate information from master takeoff file"""
    
    master_file = r"C:\Users\holme\OneDrive\Desktop\Spreadsheet CE\MASTER TAKEOFF (IMPORTANT)7.13.25.xlsm"
    
    if not os.path.exists(master_file):
        print(f"Master takeoff file not found: {master_file}")
        return
    
    try:
        # Read Excel file - try different sheet names that might contain labor info
        xl = pd.ExcelFile(master_file)
        print(f"Available sheets: {xl.sheet_names}")
        
        # Look for sheets that might contain labor information
        labor_sheets = []
        for sheet in xl.sheet_names:
            sheet_lower = sheet.lower()
            if any(keyword in sheet_lower for keyword in ['labor', 'rate', 'hour', 'cost']):
                labor_sheets.append(sheet)
        
        print(f"Potential labor sheets: {labor_sheets}")
        
        # Try to read the main sheet or first sheet
        main_sheet = xl.sheet_names[0] if xl.sheet_names else None
        if main_sheet:
            print(f"\nReading main sheet: {main_sheet}")
            df = pd.read_excel(master_file, sheet_name=main_sheet, header=None)
            
            # Look for labor-related content
            print("\nSearching for labor-related content...")
            for idx, row in df.iterrows():
                if idx > 50:  # Don't search too many rows
                    break
                    
                row_str = str(row.values).lower()
                if any(keyword in row_str for keyword in ['labor', 'hour', 'rate', 'stair', 'handrail']):
                    print(f"Row {idx}: {row.values}")
        
        # Also try specific common sheet names
        common_names = ['Labor', 'Rates', 'Settings', 'Config', 'Data']
        for name in common_names:
            if name in xl.sheet_names:
                print(f"\nReading {name} sheet:")
                df = pd.read_excel(master_file, sheet_name=name)
                print(df.head())
                
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    extract_labor_info()