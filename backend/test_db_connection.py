#!/usr/bin/env python3
"""
Test database connection and create a project manually
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_database():
    """Test database connection and create a sample project"""
    
    # Test different database URLs
    database_urls = [
        "postgresql://postgres:postgres123@localhost:5432/capitol_takeoff",
        "postgresql://postgres:postgres@localhost:5432/capitol_takeoff", 
        "sqlite:///./test_projects.db"  # Fallback to SQLite
    ]
    
    for db_url in database_urls:
        try:
            print(f"Trying database: {db_url}")
            engine = create_engine(db_url)
            
            # Test connection
            with engine.begin() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                print(f"✅ Database connection successful: {result}")
                
                # Check if tables exist
                tables_result = conn.execute(text("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'takeoff_projects'
                """))
                
                if not tables_result.fetchone():
                    print("Creating tables...")
                    # Create basic project table
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS takeoff_projects (
                            id VARCHAR(20) PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            client_name VARCHAR(255),
                            project_location VARCHAR(255),
                            description TEXT,
                            quote_number VARCHAR(100),
                            estimator VARCHAR(255),
                            project_date TIMESTAMP,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP WITH TIME ZONE
                        )
                    """))
                    print("✅ Tables created")
                
                # Test inserting a project
                conn.execute(text("""
                    INSERT INTO takeoff_projects (id, name, client_name, description, estimator)
                    VALUES (:id, :name, :client, :desc, :estimator)
                    ON CONFLICT (id) DO NOTHING
                """), {
                    'id': 'TEST-001',
                    'name': 'Database Test Project',
                    'client': 'Test Client',
                    'desc': 'Testing database connection',
                    'estimator': 'System Test'
                })
                
                # Verify the insert
                result = conn.execute(text("SELECT id, name FROM takeoff_projects WHERE id = 'TEST-001'")).fetchone()
                if result:
                    print(f"✅ Project created: {result[0]} - {result[1]}")
                    return db_url  # Return working database URL
                
        except Exception as e:
            print(f"❌ Database failed: {e}")
            continue
    
    print("❌ No database connections successful")
    return None

if __name__ == "__main__":
    working_db = test_database()
    if working_db:
        print(f"\n🎉 Use this database URL: {working_db}")
    else:
        print("\n💥 Database setup failed")