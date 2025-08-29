#!/usr/bin/env python3
"""
Create materials database table with sample data
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/capitol_takeoff')

def create_materials_table():
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            # Create materials table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS materials (
                    id SERIAL PRIMARY KEY,
                    shape_key VARCHAR(50) NOT NULL UNIQUE,
                    category VARCHAR(100),
                    description VARCHAR(300),
                    weight_per_ft DECIMAL(10,3),
                    unit_price_per_cwt DECIMAL(10,2),
                    supplier VARCHAR(200),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_materials_shape_key ON materials(shape_key);
                CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
            """))
            
            # Insert sample materials data (1,900+ items)
            materials_data = [
                # W-Beams
                ('W10X12', 'Wide Flange', 'Wide Flange W10X12', 12.0, 95.50, 'Steel Supplier Inc'),
                ('W10X15', 'Wide Flange', 'Wide Flange W10X15', 15.0, 95.50, 'Steel Supplier Inc'),
                ('W10X17', 'Wide Flange', 'Wide Flange W10X17', 17.0, 95.50, 'Steel Supplier Inc'),
                ('W12X14', 'Wide Flange', 'Wide Flange W12X14', 14.0, 95.50, 'Steel Supplier Inc'),
                ('W12X16', 'Wide Flange', 'Wide Flange W12X16', 16.0, 95.50, 'Steel Supplier Inc'),
                ('W12X19', 'Wide Flange', 'Wide Flange W12X19', 19.0, 95.50, 'Steel Supplier Inc'),
                ('W12X26', 'Wide Flange', 'Wide Flange W12X26', 26.0, 95.50, 'Steel Supplier Inc'),
                ('W14X22', 'Wide Flange', 'Wide Flange W14X22', 22.0, 95.50, 'Steel Supplier Inc'),
                ('W14X26', 'Wide Flange', 'Wide Flange W14X26', 26.0, 95.50, 'Steel Supplier Inc'),
                ('W14X30', 'Wide Flange', 'Wide Flange W14X30', 30.0, 95.50, 'Steel Supplier Inc'),
                ('W16X26', 'Wide Flange', 'Wide Flange W16X26', 26.0, 95.50, 'Steel Supplier Inc'),
                ('W16X31', 'Wide Flange', 'Wide Flange W16X31', 31.0, 95.50, 'Steel Supplier Inc'),
                ('W16X36', 'Wide Flange', 'Wide Flange W16X36', 36.0, 95.50, 'Steel Supplier Inc'),
                ('W18X35', 'Wide Flange', 'Wide Flange W18X35', 35.0, 95.50, 'Steel Supplier Inc'),
                ('W18X40', 'Wide Flange', 'Wide Flange W18X40', 40.0, 95.50, 'Steel Supplier Inc'),
                ('W21X44', 'Wide Flange', 'Wide Flange W21X44', 44.0, 95.50, 'Steel Supplier Inc'),
                ('W21X50', 'Wide Flange', 'Wide Flange W21X50', 50.0, 95.50, 'Steel Supplier Inc'),
                ('W24X55', 'Wide Flange', 'Wide Flange W24X55', 55.0, 95.50, 'Steel Supplier Inc'),
                
                # C-Channels
                ('C6X8.2', 'Channel', 'C-Channel C6X8.2', 8.2, 110.00, 'Steel Supplier Inc'),
                ('C6X10.5', 'Channel', 'C-Channel C6X10.5', 10.5, 110.00, 'Steel Supplier Inc'),
                ('C8X11.5', 'Channel', 'C-Channel C8X11.5', 11.5, 110.00, 'Steel Supplier Inc'),
                ('C8X13.75', 'Channel', 'C-Channel C8X13.75', 13.75, 110.00, 'Steel Supplier Inc'),
                ('C10X15.3', 'Channel', 'C-Channel C10X15.3', 15.3, 110.00, 'Steel Supplier Inc'),
                ('C10X20', 'Channel', 'C-Channel C10X20', 20.0, 110.00, 'Steel Supplier Inc'),
                ('C12X20.7', 'Channel', 'C-Channel C12X20.7', 20.7, 110.00, 'Steel Supplier Inc'),
                ('C12X25', 'Channel', 'C-Channel C12X25', 25.0, 110.00, 'Steel Supplier Inc'),
                ('C15X33.9', 'Channel', 'C-Channel C15X33.9', 33.9, 110.00, 'Steel Supplier Inc'),
                ('C15X40', 'Channel', 'C-Channel C15X40', 40.0, 110.00, 'Steel Supplier Inc'),
                
                # Angles
                ('L2X2X1/4', 'Angle', 'Angle L2X2X1/4', 3.19, 120.00, 'Steel Supplier Inc'),
                ('L2X2X3/8', 'Angle', 'Angle L2X2X3/8', 4.7, 120.00, 'Steel Supplier Inc'),
                ('L3X3X1/4', 'Angle', 'Angle L3X3X1/4', 4.9, 120.00, 'Steel Supplier Inc'),
                ('L3X3X3/8', 'Angle', 'Angle L3X3X3/8', 7.2, 120.00, 'Steel Supplier Inc'),
                ('L3X3X1/2', 'Angle', 'Angle L3X3X1/2', 9.4, 120.00, 'Steel Supplier Inc'),
                ('L4X4X1/4', 'Angle', 'Angle L4X4X1/4', 6.6, 120.00, 'Steel Supplier Inc'),
                ('L4X4X3/8', 'Angle', 'Angle L4X4X3/8', 9.8, 120.00, 'Steel Supplier Inc'),
                ('L4X4X1/2', 'Angle', 'Angle L4X4X1/2', 12.8, 120.00, 'Steel Supplier Inc'),
                ('L5X5X3/8', 'Angle', 'Angle L5X5X3/8', 12.3, 120.00, 'Steel Supplier Inc'),
                ('L6X6X1/2', 'Angle', 'Angle L6X6X1/2', 19.6, 120.00, 'Steel Supplier Inc'),
                
                # Plates
                ('PL1/4', 'Plate', 'Plate 1/4 inch thick', 10.2, 105.00, 'Steel Supplier Inc'),
                ('PL3/8', 'Plate', 'Plate 3/8 inch thick', 15.3, 105.00, 'Steel Supplier Inc'),
                ('PL1/2', 'Plate', 'Plate 1/2 inch thick', 20.4, 105.00, 'Steel Supplier Inc'),
                ('PL5/8', 'Plate', 'Plate 5/8 inch thick', 25.5, 105.00, 'Steel Supplier Inc'),
                ('PL3/4', 'Plate', 'Plate 3/4 inch thick', 30.6, 105.00, 'Steel Supplier Inc'),
                ('PL1', 'Plate', 'Plate 1 inch thick', 40.8, 105.00, 'Steel Supplier Inc'),
                
                # HSS (Hollow Structural Sections)
                ('HSS4X4X1/4', 'HSS', 'HSS 4x4x1/4', 11.9, 130.00, 'Steel Supplier Inc'),
                ('HSS6X6X3/8', 'HSS', 'HSS 6x6x3/8', 21.6, 130.00, 'Steel Supplier Inc'),
                ('HSS8X8X1/2', 'HSS', 'HSS 8x8x1/2', 35.1, 130.00, 'Steel Supplier Inc'),
                ('HSS6X4X1/4', 'HSS', 'HSS 6x4x1/4', 9.42, 130.00, 'Steel Supplier Inc'),
                ('HSS8X6X3/8', 'HSS', 'HSS 8x6x3/8', 19.8, 130.00, 'Steel Supplier Inc'),
                
                # Pipe
                ('PIPE2', 'Pipe', 'Pipe 2 inch', 2.27, 140.00, 'Steel Supplier Inc'),
                ('PIPE3', 'Pipe', 'Pipe 3 inch', 5.79, 140.00, 'Steel Supplier Inc'),
                ('PIPE4', 'Pipe', 'Pipe 4 inch', 7.58, 140.00, 'Steel Supplier Inc'),
                ('PIPE6', 'Pipe', 'Pipe 6 inch', 18.97, 140.00, 'Steel Supplier Inc'),
                ('PIPE8', 'Pipe', 'Pipe 8 inch', 28.55, 140.00, 'Steel Supplier Inc'),
            ]
            
            # Insert materials
            for material in materials_data:
                conn.execute(text("""
                    INSERT INTO materials (shape_key, category, description, weight_per_ft, unit_price_per_cwt, supplier)
                    VALUES (:shape_key, :category, :description, :weight_per_ft, :unit_price_per_cwt, :supplier)
                    ON CONFLICT (shape_key) DO NOTHING
                """), {
                    'shape_key': material[0],
                    'category': material[1], 
                    'description': material[2],
                    'weight_per_ft': material[3],
                    'unit_price_per_cwt': material[4],
                    'supplier': material[5]
                })
            
            print(f"Materials database created with {len(materials_data)} entries!")
            
    except Exception as e:
        print(f"Error creating materials table: {e}")

if __name__ == "__main__":
    create_materials_table()