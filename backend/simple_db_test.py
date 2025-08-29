#!/usr/bin/env python3
"""
Simple database test
"""

import os
from sqlalchemy import create_engine, text

def test_database():
    """Test database connection"""
    
    # Try SQLite first (simpler, no authentication)
    try:
        print("Testing SQLite database...")
        engine = create_engine("sqlite:///./projects.db")
        
        with engine.begin() as conn:
            # Test connection
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"Database connection successful: {result}")
            
            # Create table
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """))
            
            # Test insert
            conn.execute(text("""
                INSERT OR IGNORE INTO takeoff_projects 
                (id, name, client_name, description, estimator)
                VALUES (?, ?, ?, ?, ?)
            """), ('SQLITE-001', 'SQLite Test', 'Test Client', 'Testing SQLite', 'System'))
            
            # Verify
            result = conn.execute(text("SELECT id, name FROM takeoff_projects WHERE id = 'SQLITE-001'")).fetchone()
            if result:
                print(f"Project created: {result[0]} - {result[1]}")
                return True
                
    except Exception as e:
        print(f"SQLite failed: {e}")
    
    return False

if __name__ == "__main__":
    if test_database():
        print("SUCCESS: SQLite database working")
    else:
        print("FAILED: Database setup failed")