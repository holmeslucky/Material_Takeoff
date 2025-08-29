#!/usr/bin/env python3
"""
Add operations and coatings columns to takeoff_entries table
"""

import sqlite3
import json
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def add_columns_to_takeoff_entries():
    """Add new columns for operations and coatings to takeoff_entries table"""
    
    # Connect to database
    db_path = "capitol_takeoff.db"
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(takeoff_entries)")
        columns = [row[1] for row in cursor.fetchall()]
        
        new_columns = []
        
        # Add operations column if it doesn't exist
        if 'operations' not in columns:
            cursor.execute('''
                ALTER TABLE takeoff_entries 
                ADD COLUMN operations TEXT DEFAULT '[]'
            ''')
            new_columns.append('operations')
            print("Added 'operations' column")
        
        # Add coatings_selected column if it doesn't exist
        if 'coatings_selected' not in columns:
            cursor.execute('''
                ALTER TABLE takeoff_entries 
                ADD COLUMN coatings_selected TEXT DEFAULT '[]'
            ''')
            new_columns.append('coatings_selected')
            print("Added 'coatings_selected' column")
        
        # Add primary_coating column if it doesn't exist
        if 'primary_coating' not in columns:
            cursor.execute('''
                ALTER TABLE takeoff_entries 
                ADD COLUMN primary_coating TEXT DEFAULT ''
            ''')
            new_columns.append('primary_coating')
            print("Added 'primary_coating' column")
            
        # Add coating_cost column if it doesn't exist
        if 'coating_cost' not in columns:
            cursor.execute('''
                ALTER TABLE takeoff_entries 
                ADD COLUMN coating_cost REAL DEFAULT 0.0
            ''')
            new_columns.append('coating_cost')
            print("Added 'coating_cost' column")
            
        # Add thickness_in column if it doesn't exist
        if 'thickness_in' not in columns:
            cursor.execute('''
                ALTER TABLE takeoff_entries 
                ADD COLUMN thickness_in REAL DEFAULT 0.0
            ''')
            new_columns.append('thickness_in')
            print("Added 'thickness_in' column")
        
        # Commit changes
        conn.commit()
        
        if new_columns:
            print(f"Successfully added {len(new_columns)} new columns: {', '.join(new_columns)}")
        else:
            print("All columns already exist - no changes needed")
            
        return True
        
    except Exception as e:
        print(f"Error adding columns: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Adding operations and coatings columns to takeoff_entries table...")
    success = add_columns_to_takeoff_entries()
    
    if success:
        print("Database migration completed successfully!")
    else:
        print("Database migration failed!")
        sys.exit(1)