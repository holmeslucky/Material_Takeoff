"""
Capitol Engineering Company - Settings API
API endpoints for managing company and labor settings
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["settings"])

# In-memory settings store (would typically be in database)
_settings_store = {
    "company": {
        "name": "Capitol Engineering Company",
        "address": "724 E Southern Pacific Dr, Phoenix AZ 85034",
        "phone": "602-281-6517",
        "mobile": "951-732-1514",
        "email": "sales@capitolaz.com",
        "website": "www.capitolaz.com",
        "contact": "Blake Holmes"
    },
    "labor": {
        "base_rate": 120.0,
        "markup_percent": 35.0,
        "handling_percent": 20.0,
        "mode": "auto"
    },
    "user_preferences": {
        "auto_save": True,
        "default_project_template": "Standard Steel",
        "recent_materials_count": 20,
        "date_format": "MM/DD/YYYY",
        "show_grid_lines": True,
        "show_tooltips": True
    },
    "calculation_preferences": {
        "material_cost_rounding": 0.01,
        "labor_cost_rounding": 0.01,
        "default_units": "Imperial",
        "steel_density": 40.8
    },
    "export_settings": {
        "excel_template": "Standard",
        "report_format": "Detailed",
        "page_orientation": "Portrait",
        "auto_backup_frequency": "Weekly"
    },
    "system_config": {
        "cache_enabled": True,
        "search_result_limit": 100,
        "session_timeout_minutes": 480,
        "enable_notifications": True
    }
}

class CompanySettings(BaseModel):
    name: str
    address: str
    phone: str
    mobile: str
    email: str
    website: str
    contact: str

class LaborSettings(BaseModel):
    base_rate: float
    markup_percent: float
    handling_percent: float
    mode: str

class UserPreferences(BaseModel):
    auto_save: bool
    default_project_template: str
    recent_materials_count: int
    date_format: str
    show_grid_lines: bool
    show_tooltips: bool

class CalculationPreferences(BaseModel):
    material_cost_rounding: float
    labor_cost_rounding: float
    default_units: str
    steel_density: float

class ExportSettings(BaseModel):
    excel_template: str
    report_format: str
    page_orientation: str
    auto_backup_frequency: str

class SystemConfig(BaseModel):
    cache_enabled: bool
    search_result_limit: int
    session_timeout_minutes: int
    enable_notifications: bool

@router.get("/company")
async def get_company_settings() -> CompanySettings:
    """Get company settings"""
    return CompanySettings(**_settings_store["company"])

@router.post("/company")
async def update_company_settings(settings: CompanySettings) -> Dict[str, str]:
    """Update company settings"""
    _settings_store["company"] = settings.model_dump()
    return {"message": "Company settings updated successfully"}

@router.get("/labor")
async def get_labor_settings() -> LaborSettings:
    """Get labor settings"""
    return LaborSettings(**_settings_store["labor"])

@router.post("/labor")
async def update_labor_settings(settings: LaborSettings) -> Dict[str, str]:
    """Update labor settings"""
    _settings_store["labor"] = settings.model_dump()
    return {"message": "Labor settings updated successfully"}

@router.get("/user-preferences")
async def get_user_preferences() -> UserPreferences:
    """Get user preferences"""
    return UserPreferences(**_settings_store["user_preferences"])

@router.post("/user-preferences")
async def update_user_preferences(settings: UserPreferences) -> Dict[str, str]:
    """Update user preferences"""
    _settings_store["user_preferences"] = settings.model_dump()
    return {"message": "User preferences updated successfully"}

@router.get("/calculation-preferences")
async def get_calculation_preferences() -> CalculationPreferences:
    """Get calculation preferences"""
    return CalculationPreferences(**_settings_store["calculation_preferences"])

@router.post("/calculation-preferences")
async def update_calculation_preferences(settings: CalculationPreferences) -> Dict[str, str]:
    """Update calculation preferences"""
    _settings_store["calculation_preferences"] = settings.model_dump()
    return {"message": "Calculation preferences updated successfully"}

@router.get("/export-settings")
async def get_export_settings() -> ExportSettings:
    """Get export settings"""
    return ExportSettings(**_settings_store["export_settings"])

@router.post("/export-settings")
async def update_export_settings(settings: ExportSettings) -> Dict[str, str]:
    """Update export settings"""
    _settings_store["export_settings"] = settings.model_dump()
    return {"message": "Export settings updated successfully"}

@router.get("/system-config")
async def get_system_config() -> SystemConfig:
    """Get system configuration"""
    return SystemConfig(**_settings_store["system_config"])

@router.post("/system-config")
async def update_system_config(settings: SystemConfig) -> Dict[str, str]:
    """Update system configuration"""
    _settings_store["system_config"] = settings.model_dump()
    return {"message": "System configuration updated successfully"}