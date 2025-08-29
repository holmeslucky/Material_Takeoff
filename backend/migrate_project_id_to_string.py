"""
Migration script to change project ID from integer to string
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.models.takeoff import Base

def migrate_database():
    """Migrate the database to use string project IDs"""
    
    database_url = os.getenv("DATABASE_URL", "sqlite:///./takeoff.db")
    engine = create_engine(database_url)
    
    print("Starting database migration...")
    
    try:
        with engine.begin() as conn:
            # Drop existing tables to avoid schema conflicts
            print("Dropping existing tables...")
            conn.execute(text("DROP TABLE IF EXISTS takeoff_entries"))
            conn.execute(text("DROP TABLE IF EXISTS takeoff_projects"))
            
            # Create new tables with updated schema
            print("Creating tables with new schema...")
            Base.metadata.create_all(engine)
            
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    migrate_database()