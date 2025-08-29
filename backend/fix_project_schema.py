"""
Fix PostgreSQL project schema to use string IDs
"""

import os
import sys
from sqlalchemy import create_engine, text

def fix_project_schema():
    """Fix the project schema in PostgreSQL to use string IDs"""
    
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5432/capitol_takeoff")
    engine = create_engine(database_url)
    
    print("Fixing PostgreSQL project schema...")
    
    try:
        with engine.begin() as conn:
            # Drop existing takeoff tables to recreate with correct schema
            print("Dropping existing takeoff tables...")
            conn.execute(text("DROP TABLE IF EXISTS takeoff_entries CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS takeoff_projects CASCADE"))
            
            # Create takeoff_projects table with string ID
            print("Creating takeoff_projects table with string ID...")
            conn.execute(text("""
                CREATE TABLE takeoff_projects (
                    id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    client_name VARCHAR(255),
                    quote_number VARCHAR(100),
                    estimator VARCHAR(255),
                    project_location VARCHAR(255),
                    project_date TIMESTAMP,
                    project_number VARCHAR(100),
                    labor_mode VARCHAR(20) DEFAULT 'auto',
                    default_labor_rate FLOAT DEFAULT 120.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """))
            
            # Create takeoff_entries table with string project_id foreign key
            print("Creating takeoff_entries table...")
            conn.execute(text("""
                CREATE TABLE takeoff_entries (
                    id SERIAL PRIMARY KEY,
                    project_id VARCHAR(20) NOT NULL REFERENCES takeoff_projects(id) ON DELETE CASCADE,
                    qty INTEGER NOT NULL DEFAULT 1,
                    shape_key VARCHAR(50) NOT NULL,
                    description VARCHAR(300),
                    length_ft FLOAT NOT NULL DEFAULT 0.0,
                    width_ft FLOAT DEFAULT 0.0,
                    weight_per_ft FLOAT DEFAULT 0.0,
                    unit_price_per_cwt FLOAT DEFAULT 0.0,
                    category VARCHAR(100),
                    total_weight_lbs FLOAT DEFAULT 0.0,
                    total_weight_tons FLOAT DEFAULT 0.0,
                    total_price FLOAT DEFAULT 0.0,
                    labor_hours FLOAT DEFAULT 0.0,
                    labor_rate FLOAT DEFAULT 120.0,
                    labor_cost FLOAT DEFAULT 0.0,
                    labor_mode VARCHAR(20) DEFAULT 'auto',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            print("Schema fix completed successfully!")
            
    except Exception as e:
        print(f"Schema fix failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    fix_project_schema()