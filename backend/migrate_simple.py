#!/usr/bin/env python3
"""
Simple Database Migration: Add Blake's Material Fields
"""

import sys
from pathlib import Path
from sqlalchemy import text, inspect
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, engine
from app.models.material import Material

def check_and_add_columns():
    """Add new columns if they don't exist"""
    print("Checking and adding new columns...")
    
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('materials')]
        print(f"Current columns: {len(existing_columns)}")
        
        # New columns to add
        new_columns = {
            'subcategory': 'VARCHAR(50)',
            'specs_standard': 'VARCHAR(100)', 
            'base_price_usd': 'FLOAT',
            'size_dimensions': 'VARCHAR(200)',
            'schedule_class': 'VARCHAR(50)',
            'finish_coating': 'VARCHAR(100)',
            'weight_per_uom': 'FLOAT',
            'unit_of_measure': 'VARCHAR(20)',
            'source_system': 'VARCHAR(20)',
            'sku_part_number': 'VARCHAR(100)',
            'notes': 'TEXT',
            'price_confidence': 'VARCHAR(20)',
            'last_price_update': 'DATETIME'
        }
        
        added_count = 0
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE materials ADD COLUMN {column_name} {column_type}"
                    db.execute(text(sql))
                    print(f"  Added: {column_name}")
                    added_count += 1
                except Exception as e:
                    print(f"  Error adding {column_name}: {e}")
            else:
                print(f"  Exists: {column_name}")
        
        if added_count > 0:
            db.commit()
            print(f"Added {added_count} new columns")
        else:
            print("No new columns needed")
        
        # Set defaults for existing materials
        print("Setting defaults for existing materials...")
        db.execute(text("UPDATE materials SET source_system = 'legacy' WHERE source_system IS NULL"))
        db.execute(text("UPDATE materials SET unit_of_measure = 'ft' WHERE unit_of_measure IS NULL"))
        db.execute(text("UPDATE materials SET price_confidence = 'high' WHERE price_confidence IS NULL"))
        db.commit()
        
        # Verify
        final_count = len(inspector.get_columns('materials'))
        material_count = db.query(Material).count()
        
        print(f"Final schema: {final_count} columns")
        print(f"Materials: {material_count}")
        print("Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("Blake's Material Database Migration")
    print("=" * 40)
    
    success = check_and_add_columns()
    if success:
        print("Ready for Blake's data import!")
    else:
        print("Migration failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())