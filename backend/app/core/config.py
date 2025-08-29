import os
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./capitol_takeoff.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "CHANGE-THIS-IN-PRODUCTION-RAILWAY-ENV-VARS")
    jwt_exp_minutes: int = int(os.getenv("JWT_EXP_MINUTES", "60"))
    cors_origins: list[str] = [o for o in os.getenv("CORS_ORIGINS", "*" if os.getenv("ENVIRONMENT") == "production" else "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178,http://localhost:5179").split(",") if o]
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@local")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "Admin123!")
    env: str = os.getenv("ENV", "staging")
    
    # Indolent Designs Company Profile
    company_name: str = os.getenv("COMPANY_NAME", "Indolent Designs")
    company_address: str = os.getenv("COMPANY_ADDRESS", "742 Evergreen Terrace, Springfield")
    company_phone: str = os.getenv("COMPANY_PHONE", "951-732-1514")
    company_mobile: str = os.getenv("COMPANY_MOBILE", "951-732-1514")
    company_contact: str = os.getenv("COMPANY_CONTACT", "Blake Holmes")
    company_email: str = os.getenv("COMPANY_EMAIL", "indolentforge@gmail.com")
    company_website: str = os.getenv("COMPANY_WEBSITE", "https://indolent.neocities.org/")
    
    # OpenAI Configuration (Phase 5)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()