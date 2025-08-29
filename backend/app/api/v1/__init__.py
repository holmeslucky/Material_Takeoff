from fastapi import APIRouter
from . import materials, takeoff, takeoff_locked, projects, ai, labor, labor_management, settings, nesting, proposals, templates

api_router = APIRouter()
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(takeoff.router, prefix="/takeoff", tags=["takeoff"])
api_router.include_router(takeoff_locked.router, prefix="/takeoff-locked", tags=["takeoff-locked"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(labor.router, prefix="/labor", tags=["labor"])
api_router.include_router(labor_management.router, prefix="/labor-mgmt", tags=["labor-management"])
api_router.include_router(settings.router, tags=["settings"])
api_router.include_router(nesting.router, prefix="/nesting", tags=["nesting"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])