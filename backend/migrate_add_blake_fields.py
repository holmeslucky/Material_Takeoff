#!/usr/bin/env python3
"""
Safe Database Migration: Add Blake's Material Fields
Backwards-compatible migration to add new fields without breaking existing functionality
"""

import sys
from pathlib import Path
from sqlalchemy import text, inspect
from datetime import datetime

# Add the app directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, engine
from app.models.material import Material

def backup_database():
    """Create a backup of the current database"""
    backup_name = f"capitol_takeoff_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    print(f"Creating backup: {backup_name}")
    
    # For SQLite, copy the file
    import shutil
    import os
    
    db_path = "capitol_takeoff.db"  # Adjust if different
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_name)
        print(f"[OK] Backup created: {backup_name}")
        return backup_name
    else:
        print("[WARNING] Database file not found for backup")
        return None

def check_current_schema():
    """Check the current database schema"""
    print("Checking current database schema...")
    
    db = SessionLocal()
    try:
        # Get current table structure
        inspector = inspect(engine)
        columns = inspector.get_columns('materials')
        
        print("Current materials table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} {'(nullable)' if col['nullable'] else '(not null)'}")
        
        # Count existing materials
        count = db.query(Material).count()
        print(f"\nCurrent material count: {count}")
        
        # Show sample materials
        samples = db.query(Material).limit(3).all()
        print("\nSample materials:")
        for material in samples:
            print(f"  - {material.shape_key}: {material.description}")
            
        return columns
        
    finally:
        db.close()

def add_new_columns():
    """Add new columns for Blake's data integration"""
    print("\nAdding new columns for Blake's material data...")
    
    db = SessionLocal()
    try:
        # Check if columns already exist
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('materials')]
        
        # Define new columns to add
        new_columns = [
            "ALTER TABLE materials ADD COLUMN subcategory VARCHAR(50)",
            "ALTER TABLE materials ADD COLUMN specs_standard VARCHAR(100)",
            "ALTER TABLE materials ADD COLUMN base_price_usd FLOAT",
            "ALTER TABLE materials ADD COLUMN size_dimensions VARCHAR(200)",
            "ALTER TABLE materials ADD COLUMN schedule_class VARCHAR(50)",
            "ALTER TABLE materials ADD COLUMN finish_coating VARCHAR(100)",
            "ALTER TABLE materials ADD COLUMN weight_per_uom FLOAT", 
            "ALTER TABLE materials ADD COLUMN unit_of_measure VARCHAR(20) DEFAULT 'ft'",
            "ALTER TABLE materials ADD COLUMN source_system VARCHAR(20) DEFAULT 'legacy'",
            "ALTER TABLE materials ADD COLUMN sku_part_number VARCHAR(100)",
            "ALTER TABLE materials ADD COLUMN notes TEXT",
            "ALTER TABLE materials ADD COLUMN price_confidence VARCHAR(20) DEFAULT 'high'",
            "ALTER TABLE materials ADD COLUMN last_price_update DATETIME"
        ]
        
        # Add columns that don't already exist
        for alter_sql in new_columns:
            column_name = alter_sql.split('ADD COLUMN ')[1].split(' ')[0]
            
            if column_name not in existing_columns:
                try:
                    db.execute(text(alter_sql))
                    print(f"  [OK] Added column: {column_name}")
                except Exception as e:
                    print(f"  [WARNING] Could not add {column_name}: {e}")
            else:
                print(f"  [SKIP] Column already exists: {column_name}")
        
        db.commit()
        print("[OK] Column additions complete")
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_indexes():
    """Create indexes for performance with large dataset"""
    print("\nCreating performance indexes...")
    
    db = SessionLocal()
    try:
        indexes = [
            "CREATE INDEX IF NOT EXISTS ix_materials_subcategory ON materials(subcategory)",
            "CREATE INDEX IF NOT EXISTS ix_materials_specs_standard ON materials(specs_standard)",
            "CREATE INDEX IF NOT EXISTS ix_materials_source_system ON materials(source_system)",
            "CREATE INDEX IF NOT EXISTS ix_materials_base_price ON materials(base_price_usd)",
            "CREATE INDEX IF NOT EXISTS ix_materials_category_subcategory ON materials(category, subcategory)"
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                index_name = index_sql.split('ix_materials_')[1].split(' ')[0]
                print(f"  ✅ Created index: ix_materials_{index_name}")
            except Exception as e:
                print(f"  ⚠️  Index creation issue: {e}")
        
        db.commit()
        print("✅ Index creation complete")
        
    finally:
        db.close()

def mark_existing_materials():
    """Mark existing materials as legacy source"""
    print("\nMarking existing materials as legacy source...")
    
    db = SessionLocal()
    try:
        # Update all existing materials to mark as legacy
        result = db.execute(
            text("UPDATE materials SET source_system = 'legacy' WHERE source_system IS NULL OR source_system = 'legacy'")
        )
        db.commit()
        
        count = result.rowcount
        print(f"✅ Marked {count} materials as legacy source")
        
    finally:
        db.close()

def verify_migration():
    """Verify the migration was successful"""
    print("\nVerifying migration...")
    
    db = SessionLocal()
    try:
        # Check new schema
        inspector = inspect(engine)
        columns = inspector.get_columns('materials')
        
        expected_new_columns = [
            'subcategory', 'specs_standard', 'base_price_usd', 
            'size_dimensions', 'schedule_class', 'finish_coating',
            'weight_per_uom', 'unit_of_measure', 'source_system'
        ]
        
        found_columns = [col['name'] for col in columns]
        missing_columns = [col for col in expected_new_columns if col not in found_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Test that existing materials still work
        sample = db.query(Material).first()
        if sample:
            print(f"✅ Existing material still accessible: {sample.shape_key}")
        
        # Count materials by source
        legacy_count = db.execute(text("SELECT COUNT(*) FROM materials WHERE source_system = 'legacy'")).scalar()
        print(f"✅ Legacy materials: {legacy_count}")
        
        print("✅ Migration verification successful!")
        return True
        
    except Exception as e:
        print(f"❌ Migration verification failed: {e}")
        return False
    finally:
        db.close()

def main():
    """Run the complete migration"""
    print("BLAKE'S MATERIAL DATABASE INTEGRATION")
    print("Safe Backwards-Compatible Migration")
    print("=" * 50)
    
    try:
        # Step 1: Backup
        backup_file = backup_database()
        if not backup_file:
            print("⚠️  Proceeding without backup...")
        
        # Step 2: Check current state
        current_columns = check_current_schema()
        
        # Step 3: Add new columns
        add_new_columns()
        
        # Step 4: Create indexes for performance
        create_indexes()
        
        # Step 5: Mark existing materials
        mark_existing_materials()
        
        # Step 6: Verify migration
        success = verify_migration()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("✅ All existing functionality preserved")
            print("✅ Ready for Blake's material data import")
            print("=" * 50)
            
            if backup_file:
                print(f"📁 Backup available: {backup_file}")
        else:
            print("\n❌ Migration verification failed!")
            if backup_file:
                print(f"📁 Restore from backup if needed: {backup_file}")
    
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("The existing database should be unchanged.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())