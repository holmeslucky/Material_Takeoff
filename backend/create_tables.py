from app.core.database import engine, Base
from app.models.takeoff import TakeoffProject, TakeoffEntry
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created!")
