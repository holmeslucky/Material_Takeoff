#!/usr/bin/env python3
"""
Capitol Engineering Company - Material Database Migration
Migrates materials from desktop SQLite to PostgreSQL web database
"""

import sqlite3
import asyncio
import asyncpg
import os
from datetime import datetime
from typing import List, Dict, Any

# Database connection settings
SQLITE_DB_PATH = "../../takeoff_data_BACKUP_WEB_MIGRATION.db"
POSTGRES_URL = "postgresql://postgres:postgres123@localhost:5432/capitol_takeoff"

class MaterialMigration:
    def __init__(self):
        self.sqlite_conn = None
        self.postgres_conn = None
        self.migrated_count = 0
        
    async def connect_databases(self):
        """Connect to both SQLite and PostgreSQL databases"""
        try:
            # Connect to SQLite (desktop backup)
            self.sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
            self.sqlite_conn.row_factory = sqlite3.Row
            print(f"[OK] Connected to SQLite: {SQLITE_DB_PATH}")
            
            # Connect to PostgreSQL (web database)
            self.postgres_conn = await asyncpg.connect(POSTGRES_URL)
            print(f"[OK] Connected to PostgreSQL")
            
        except Exception as e:
            print(f"[ERROR] Database connection error: {e}")
            raise
    
    async def analyze_sqlite_structure(self):
        """Analyze the structure of the SQLite database"""
        print("\n[INFO] Analyzing SQLite Database Structure...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"    Columns ({len(columns)}):")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
                
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}")
            print()
    
    async def extract_materials(self) -> List[Dict[str, Any]]:
        """Extract materials from SQLite database"""
        print("📤 Extracting materials from SQLite...")
        
        cursor = self.sqlite_conn.cursor()
        
        # Try common table names for materials
        possible_tables = ['materials', 'steel_shapes', 'shapes', 'inventory', 'material_database']
        materials_table = None
        
        for table in possible_tables:
            try:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                materials_table = table
                print(f"✓ Found materials table: {table}")
                break
            except sqlite3.OperationalError:
                continue
        
        if not materials_table:
            # Get first table as fallback
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                materials_table = tables[0][0]
                print(f"⚠️  Using first table as materials: {materials_table}")
        
        if not materials_table:
            raise Exception("No materials table found in SQLite database")
        
        # Extract all materials
        cursor.execute(f"SELECT * FROM {materials_table}")
        rows = cursor.fetchall()
        
        materials = []
        for row in rows:
            # Convert SQLite row to dictionary
            material = dict(row)
            
            # Standardize column names and ensure required fields
            standardized = {
                'shape_key': self._get_field(material, ['shape_key', 'shape', 'key', 'material_key', 'id']),
                'category': self._get_field(material, ['category', 'type', 'shape_type', 'material_type']),
                'description': self._get_field(material, ['description', 'desc', 'name', 'material_name']),
                'weight_per_ft': float(self._get_field(material, ['weight_per_ft', 'weight', 'wt_per_ft', 'unit_weight']) or 0),
                'dimensions': self._get_field(material, ['dimensions', 'size', 'specs', 'specification']),
                'unit_price_per_cwt': float(self._get_field(material, ['unit_price_per_cwt', 'price', 'cost', 'unit_price']) or 0),
                'supplier': self._get_field(material, ['supplier', 'vendor', 'source']) or 'Capitol Steel',
                'last_updated': datetime.now().isoformat()
            }
            
            # Skip if no shape_key (required field)
            if not standardized['shape_key']:
                continue
                
            # Set default category if missing
            if not standardized['category']:
                standardized['category'] = self._guess_category(standardized['shape_key'])
            
            # Set default description if missing  
            if not standardized['description']:
                standardized['description'] = f"{standardized['category']} {standardized['shape_key']}"
            
            materials.append(standardized)
        
        print(f"✓ Extracted {len(materials)} materials")
        return materials
    
    def _get_field(self, material: Dict[str, Any], possible_names: List[str]) -> Any:
        """Get field value trying multiple possible column names"""
        for name in possible_names:
            if name in material and material[name] is not None:
                return material[name]
            # Try case variations
            for key in material.keys():
                if key.lower() == name.lower():
                    return material[key]
        return None
    
    def _guess_category(self, shape_key: str) -> str:
        """Guess material category from shape key"""
        shape_key = shape_key.upper()
        
        if shape_key.startswith('W'):
            return 'Wide Flange'
        elif shape_key.startswith('PL') or 'PLATE' in shape_key:
            return 'Plate'  
        elif shape_key.startswith('L'):
            return 'Angle'
        elif shape_key.startswith('HSS') or shape_key.startswith('TS'):
            return 'HSS/Tube'
        elif shape_key.startswith('C') and not shape_key.startswith('CH'):
            return 'Channel'
        elif shape_key.startswith('CH') or 'CHANNEL' in shape_key:
            return 'Channel'
        elif 'PIPE' in shape_key:
            return 'Pipe'
        elif 'BAR' in shape_key:
            return 'Bar'
        else:
            return 'Other'
    
    async def setup_postgres_tables(self):
        """Create materials table in PostgreSQL if it doesn't exist"""
        print("🔧 Setting up PostgreSQL tables...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            shape_key VARCHAR(50) UNIQUE NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            weight_per_ft DECIMAL(10,3) NOT NULL DEFAULT 0,
            dimensions VARCHAR(200),
            unit_price_per_cwt DECIMAL(10,2) NOT NULL DEFAULT 0,
            supplier VARCHAR(100) DEFAULT 'Capitol Steel',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
        CREATE INDEX IF NOT EXISTS idx_materials_shape_key ON materials(shape_key);
        CREATE INDEX IF NOT EXISTS idx_materials_supplier ON materials(supplier);
        """
        
        await self.postgres_conn.execute(create_table_sql)
        print("✓ PostgreSQL materials table ready")
    
    async def migrate_materials(self, materials: List[Dict[str, Any]]):
        """Insert materials into PostgreSQL database"""
        print(f"📥 Migrating {len(materials)} materials to PostgreSQL...")
        
        # Clear existing materials (fresh migration)
        await self.postgres_conn.execute("DELETE FROM materials")
        print("✓ Cleared existing materials")
        
        # Batch insert materials
        batch_size = 100
        for i in range(0, len(materials), batch_size):
            batch = materials[i:i + batch_size]
            
            insert_sql = """
            INSERT INTO materials (
                shape_key, category, description, weight_per_ft, 
                dimensions, unit_price_per_cwt, supplier, last_updated
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (shape_key) DO UPDATE SET
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                weight_per_ft = EXCLUDED.weight_per_ft,
                dimensions = EXCLUDED.dimensions,
                unit_price_per_cwt = EXCLUDED.unit_price_per_cwt,
                supplier = EXCLUDED.supplier,
                last_updated = EXCLUDED.last_updated
            """
            
            for material in batch:
                try:
                    await self.postgres_conn.execute(
                        insert_sql,
                        material['shape_key'],
                        material['category'], 
                        material['description'],
                        material['weight_per_ft'],
                        material['dimensions'],
                        material['unit_price_per_cwt'],
                        material['supplier'],
                        material['last_updated']
                    )
                    self.migrated_count += 1
                except Exception as e:
                    print(f"⚠️  Error inserting {material['shape_key']}: {e}")
            
            print(f"✓ Migrated batch {i//batch_size + 1}/{(len(materials)-1)//batch_size + 1}")
    
    async def verify_migration(self):
        """Verify the migration was successful"""
        print("\n🔍 Verifying migration...")
        
        # Count materials by category
        count_sql = """
        SELECT category, COUNT(*) as count 
        FROM materials 
        GROUP BY category 
        ORDER BY count DESC
        """
        
        results = await self.postgres_conn.fetch(count_sql)
        
        total_count = sum(row['count'] for row in results)
        
        print(f"✓ Total materials migrated: {total_count}")
        print("Materials by category:")
        for row in results:
            print(f"  • {row['category']}: {row['count']}")
        
        # Sample materials
        sample_sql = "SELECT shape_key, category, description, unit_price_per_cwt FROM materials LIMIT 5"
        samples = await self.postgres_conn.fetch(sample_sql)
        
        print("\nSample materials:")
        for material in samples:
            print(f"  • {material['shape_key']} ({material['category']}) - ${material['unit_price_per_cwt']}/CWT")
    
    async def close_connections(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.postgres_conn:
            await self.postgres_conn.close()
        print("✓ Database connections closed")

async def main():
    """Main migration process"""
    print("🏗️  Capitol Engineering - Material Database Migration")
    print("=" * 60)
    
    migration = MaterialMigration()
    
    try:
        # Step 1: Connect to databases
        await migration.connect_databases()
        
        # Step 2: Analyze SQLite structure
        await migration.analyze_sqlite_structure()
        
        # Step 3: Extract materials from SQLite
        materials = await migration.extract_materials()
        
        # Step 4: Setup PostgreSQL tables
        await migration.setup_postgres_tables()
        
        # Step 5: Migrate materials
        await migration.migrate_materials(materials)
        
        # Step 6: Verify migration
        await migration.verify_migration()
        
        print(f"\n🎉 Migration Complete!")
        print(f"Successfully migrated {migration.migrated_count} materials")
        print("Capitol Takeoff material database is ready for web application!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False
        
    finally:
        await migration.close_connections()
    
    return True

if __name__ == "__main__":
    # Run the migration
    success = asyncio.run(main())
    if not success:
        exit(1)