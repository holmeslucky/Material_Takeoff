from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Import all models here to ensure they're registered with Base
from app.models import material, takeoff, labor_operation, coating_system, labor_settings, nesting, template