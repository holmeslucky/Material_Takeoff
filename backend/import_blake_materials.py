#!/usr/bin/env python3
"""
Blake's Comprehensive Material Database Import
Import 15,047 materials with smart merging and category mapping
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.material import Material

def load_blake_data():
    """Load Blake's comprehensive material data"""
    print("Loading Blake's material database...")
    
    # Load the master list  
    csv_path = Path(__file__).parent.parent.parent / "BLAKE_MAT_LIST_Master_List.csv"
    
    try:
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df):,} materials from Blake's database")
        return df
    except Exception as e:
        print(f"Error loading Blake's data: {e}")
        return None

def create_shape_key(row):
    """Create a unique shape_key for Blake's materials"""
    category = str(row.get('Category', '')).strip()
    subcategory = str(row.get('Subcategory', '')).strip()  
    designation = str(row.get('Designation', '')).strip()
    
    # Remove quotes and clean up designation
    designation = designation.replace('"', '').replace("'", "")
    
    # Create shape key based on subcategory
    if subcategory == 'Fitting':
        return f"FITTING-{designation}"
    elif subcategory == 'Pipe':
        return f"PIPE-{designation}"
    elif subcategory == 'Valve':
        return f"VALVE-{designation}"
    elif subcategory == 'Flange':
        return f"FLANGE-{designation}"
    elif subcategory == 'Component':
        return f"COMP-{designation}"
    elif subcategory == 'Plate':
        return f"PLATE-{designation}"
    elif subcategory == 'Structural':
        return f"STRUCT-{designation}"
    else:
        return f"{subcategory.upper()}-{designation}" if subcategory else designation

def map_blake_category(row):
    """Map Blake's categories to our system"""
    subcategory = str(row.get('Subcategory', '')).strip()
    
    # Map Blake's subcategories to our categories
    category_mapping = {
        'Fitting': 'Fitting',
        'Pipe': 'Pipe', 
        'Valve': 'Valve',
        'Flange': 'Flange',
        'Component': 'Component',
        'Plate': 'Plate',
        'Structural': 'Wide Flange',  # Map to existing structural category
    }
    
    return category_mapping.get(subcategory, 'General')

def safe_float(value):
    """Safely convert value to float"""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_str(value):
    """Safely convert value to string"""
    if pd.isna(value) or value is None:
        return None
    return str(value).strip() if str(value).strip() else None

def import_blake_materials(df, batch_size=500):
    """Import Blake's materials in batches"""
    print("Starting Blake's material import...")
    
    db = SessionLocal()
    try:
        # Check existing Blake materials to avoid duplicates
        existing_blake = {m.shape_key for m in db.query(Material).filter(Material.source_system == 'blake')}
        
        imported_count = 0
        skipped_count = 0
        
        # Process in batches
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            print(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_df)} materials)...")
            
            batch_materials = []
            
            for _, row in batch_df.iterrows():
                try:
                    # Create shape key
                    shape_key = create_shape_key(row)
                    
                    if not shape_key or shape_key in existing_blake:
                        skipped_count += 1
                        continue
                    
                    # Create material object
                    material = Material(
                        shape_key=shape_key,
                        description=safe_str(row.get('Designation')),
                        category=map_blake_category(row),
                        material_type=safe_str(row.get('Material')),
                        grade=safe_str(row.get('Specs/Standard')),
                        
                        # Blake's specific fields
                        subcategory=safe_str(row.get('Subcategory')),
                        specs_standard=safe_str(row.get('Specs/Standard')),
                        base_price_usd=safe_float(row.get('Base_Price')),
                        size_dimensions=safe_str(row.get('Size/Dimensions')),
                        schedule_class=safe_str(row.get('Schedule/Class')),
                        finish_coating=safe_str(row.get('Finish/Coating')),
                        weight_per_uom=safe_float(row.get('Weight_per_UoM')),
                        unit_of_measure=safe_str(row.get('UoM')) or 'each',
                        source_system='blake',
                        sku_part_number=safe_str(row.get('SKU/Part')),
                        notes=safe_str(row.get('Notes')),
                        price_confidence='high',  # Blake's data is high confidence
                        last_price_update=datetime.now(timezone.utc),
                        
                        # Supplier info
                        supplier=safe_str(row.get('Source/List')) or 'Blake Database',
                        
                        # Set as commonly used for popular items
                        commonly_used=safe_float(row.get('Base_Price', 0)) and safe_float(row.get('Base_Price')) < 100
                    )
                    
                    batch_materials.append(material)
                    existing_blake.add(shape_key)  # Prevent duplicates within this import
                    
                except Exception as e:
                    print(f"    Error processing row: {e}")
                    skipped_count += 1
                    continue
            
            # Add batch to database
            if batch_materials:
                db.add_all(batch_materials)
                db.commit()
                imported_count += len(batch_materials)
                
                print(f"    Imported {len(batch_materials)} materials")
        
        print(f"\nImport complete!")
        print(f"  Imported: {imported_count:,} materials")
        print(f"  Skipped: {skipped_count:,} materials")
        print(f"  Total in database: {db.query(Material).count():,} materials")
        
        return imported_count
        
    except Exception as e:
        print(f"Import failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def verify_import():
    """Verify the import was successful"""
    print("\nVerifying import...")
    
    db = SessionLocal()
    try:
        # Count materials by source
        total_count = db.query(Material).count()
        legacy_count = db.query(Material).filter(Material.source_system == 'legacy').count()
        blake_count = db.query(Material).filter(Material.source_system == 'blake').count()
        
        print(f"Total materials: {total_count:,}")
        print(f"Legacy materials: {legacy_count:,}")
        print(f"Blake materials: {blake_count:,}")
        
        # Show breakdown by category
        print("\nCategory breakdown (Blake materials):")
        categories = db.query(Material.category, Material.subcategory).filter(
            Material.source_system == 'blake'
        ).distinct().all()
        
        for category, subcategory in sorted(categories):
            if category and subcategory:
                count = db.query(Material).filter(
                    Material.source_system == 'blake',
                    Material.category == category,
                    Material.subcategory == subcategory
                ).count()
                print(f"  {category}/{subcategory}: {count:,}")
        
        # Show sample expensive items
        print("\nSample high-value items:")
        expensive = db.query(Material).filter(
            Material.source_system == 'blake',
            Material.base_price_usd > 200
        ).limit(5).all()
        
        for material in expensive:
            print(f"  {material.shape_key}: ${material.base_price_usd:.2f} ({material.category_display})")
        
        return True
        
    finally:
        db.close()

def main():
    """Main import function"""
    print("BLAKE'S COMPREHENSIVE MATERIAL DATABASE IMPORT")
    print("=" * 60)
    
    # Load Blake's data
    df = load_blake_data()
    if df is None:
        print("Failed to load Blake's data")
        return 1
    
    # Show data overview
    print(f"\nData overview:")
    print(f"  Total materials: {len(df):,}")
    print(f"  Categories: {df['Category'].nunique()}")
    print(f"  Subcategories: {df['Subcategory'].nunique()}")
    print(f"  With pricing: {df['Base_Price'].notna().sum():,}")
    
    # Ask for confirmation
    response = input("\nProceed with import? (y/N): ").strip().lower()
    if response != 'y':
        print("Import cancelled")
        return 0
    
    # Import materials
    try:
        imported_count = import_blake_materials(df)
        
        if imported_count > 0:
            verify_import()
            print("\n" + "=" * 60)
            print("BLAKE'S MATERIAL DATABASE SUCCESSFULLY INTEGRATED!")
            print("Your system now has comprehensive pipe, fitting, valve, and component pricing!")
            print("=" * 60)
        
    except Exception as e:
        print(f"Import failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())