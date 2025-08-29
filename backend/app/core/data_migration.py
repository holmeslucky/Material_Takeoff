"""
Data Migration Script - Import hardcoded labor operations and coating systems to database
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.labor_operation import LaborOperation, OperationType
from app.models.coating_system import CoatingSystem, CoatingType
from app.models.labor_settings import LaborSettings
from app.core.database import SessionLocal, engine, Base

def migrate_labor_data():
    """Migrate hardcoded labor data to database"""
    # First ensure tables exist by creating them explicitly
    print("Creating labor management tables...")
    
    # Import the models to make sure they're registered
    from app.models.labor_operation import LaborOperation
    from app.models.coating_system import CoatingSystem 
    from app.models.labor_settings import LaborSettings
    
    # Create the tables
    LaborOperation.__table__.create(engine, checkfirst=True)
    CoatingSystem.__table__.create(engine, checkfirst=True)
    LaborSettings.__table__.create(engine, checkfirst=True)
    print("Tables created successfully")
    
    db = SessionLocal()
    try:
        print("Starting labor data migration...")
        
        # Check if data already exists (wrap in try/except for safety)
        try:
            operation_count = db.query(LaborOperation).count()
        except:
            operation_count = 0
            
        if operation_count > 0:
            print("Labor operations already exist, skipping migration")
        else:
            # Import labor operations from takeoff_service.py constants
            labor_operations = [
                {
                    "name": "Pressbrake Forming",
                    "rate": Decimal("0.5"),
                    "operation_type": OperationType.per_ft,
                    "description": "Sheet metal forming using press brake",
                    "unit_display": "per linear foot"
                },
                {
                    "name": "Roll Forming", 
                    "rate": Decimal("0.5"),
                    "operation_type": OperationType.per_ft,
                    "description": "Continuous forming of metal sheets",
                    "unit_display": "per linear foot"
                },
                {
                    "name": "Saw Cutting",
                    "rate": Decimal("0.18"),
                    "operation_type": OperationType.per_ft,
                    "description": "Metal cutting using saw",
                    "unit_display": "per linear foot"
                },
                {
                    "name": "Drill & Punch",
                    "rate": Decimal("0.24"),
                    "operation_type": OperationType.per_ft,
                    "description": "Drilling and punching holes",
                    "unit_display": "per linear foot"
                },
                {
                    "name": "Dragon Plasma Cutting",
                    "rate": Decimal("0.18"),
                    "operation_type": OperationType.per_ft,
                    "description": "CNC plasma cutting",
                    "unit_display": "per linear foot"
                },
                {
                    "name": "Beam Line Cutting",
                    "rate": Decimal("1.0"),
                    "operation_type": OperationType.per_piece,
                    "description": "Structural beam cutting and preparation",
                    "unit_display": "per piece"
                },
                {
                    "name": "Shearing",
                    "rate": Decimal("0.0667"),
                    "operation_type": OperationType.per_ft,
                    "description": "Metal shearing operations",
                    "unit_display": "per linear foot"
                }
            ]
            
            for op_data in labor_operations:
                operation = LaborOperation(**op_data)
                db.add(operation)
            
            print(f"Added {len(labor_operations)} labor operations")
        
        # Check if coating data already exists
        try:
            coating_count = db.query(CoatingSystem).count()
        except:
            coating_count = 0
            
        if coating_count > 0:
            print("Coating systems already exist, skipping migration")
        else:
            # Import coating systems from takeoff_service.py constants
            coating_systems = [
                {
                    "name": "Shop Coating",
                    "coating_type": CoatingType.area,
                    "rate": Decimal("2.85"),
                    "description": "Standard shop-applied coating",
                    "unit_display": "per square foot"
                },
                {
                    "name": "Epoxy",
                    "coating_type": CoatingType.area,
                    "rate": Decimal("4.85"),
                    "description": "Epoxy coating system",
                    "unit_display": "per square foot"
                },
                {
                    "name": "Powder Coat",
                    "coating_type": CoatingType.area,
                    "rate": Decimal("4.85"),
                    "description": "Powder coating application",
                    "unit_display": "per square foot"
                },
                {
                    "name": "Galvanized",
                    "coating_type": CoatingType.weight,
                    "rate": Decimal("0.67"),
                    "description": "Hot-dip galvanizing",
                    "unit_display": "per pound"
                },
                {
                    "name": "None",
                    "coating_type": CoatingType.none,
                    "rate": Decimal("0"),
                    "description": "No coating applied",
                    "unit_display": "none"
                }
            ]
            
            for coating_data in coating_systems:
                coating = CoatingSystem(**coating_data)
                db.add(coating)
                
            print(f"Added {len(coating_systems)} coating systems")
        
        # Check if settings data already exists
        try:
            settings_count = db.query(LaborSettings).count()
        except:
            settings_count = 0
            
        if settings_count > 0:
            print("Labor settings already exist, skipping migration")
        else:
            # Import base settings from takeoff_service.py constants
            labor_settings = [
                {
                    "setting_key": "labor_rate_per_hour",
                    "setting_value": Decimal("120.00"),
                    "description": "Base hourly labor rate",
                    "unit": "per hour"
                },
                {
                    "setting_key": "markup_percentage",
                    "setting_value": Decimal("35.0"),
                    "description": "Project markup percentage",
                    "unit": "percentage"
                },
                {
                    "setting_key": "handling_percentage", 
                    "setting_value": Decimal("20.0"),
                    "description": "Material handling percentage",
                    "unit": "percentage"
                }
            ]
            
            for setting_data in labor_settings:
                setting = LaborSettings(**setting_data)
                db.add(setting)
                
            print(f"Added {len(labor_settings)} labor settings")
        
        db.commit()
        print("Labor data migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_labor_data()