import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.routers import health

# Create FastAPI application
app = FastAPI(
    title="Indolent Forge API",
    version="1.0.0",
    description="Professional Takeoff System API - Indolent Designs"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (in production, use Alembic migrations)
@app.on_event("startup")
async def startup_event():
    # Create tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Run labor data migration only if not in production
        if settings.env != "production":
            from app.core.data_migration import migrate_labor_data
            try:
                migrate_labor_data()
                print("Labor data migration completed")
            except Exception as migration_error:
                print(f"Labor migration failed: {migration_error}")
        else:
            print("Production mode: Skipping data migrations")
            
    except Exception as e:
        error_msg = f"Database connection failed: {e}"
        print(error_msg)
        
        # In production, database failures should be fatal
        if settings.env == "production":
            print("FATAL: Database connection required in production")
            raise e
        else:
            print("Development mode: Continuing without database")

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")

# Mount static files for production (frontend build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    # Mount assets directory (CSS, JS, images)
    assets_dir = os.path.join(static_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        print(f"✅ Serving frontend assets from: {assets_dir}")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"✅ Serving static files from: {static_dir}")
else:
    print(f"⚠️ Static directory not found: {static_dir}")

@app.get("/api")
def api_root():
    """API root endpoint"""
    return {
        "name": "Indolent Forge API",
        "version": "1.0.0",
        "environment": settings.env,
        "company": settings.company_name,
        "status": "ready"
    }

@app.get("/debug")
def debug_info():
    """Debug endpoint to check static file setup"""
    import glob
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    
    debug_data = {
        "static_dir_path": static_dir,
        "static_dir_exists": os.path.exists(static_dir),
        "current_working_directory": os.getcwd(),
        "app_file_location": __file__
    }
    
    if os.path.exists(static_dir):
        try:
            debug_data["static_dir_contents"] = os.listdir(static_dir)
            index_path = os.path.join(static_dir, "index.html")
            debug_data["index_html_exists"] = os.path.exists(index_path)
            
            # List all files in static directory
            all_files = []
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    all_files.append(os.path.relpath(os.path.join(root, file), static_dir))
            debug_data["all_static_files"] = all_files[:20]  # Limit to first 20 files
        except Exception as e:
            debug_data["static_dir_error"] = str(e)
    
    return debug_data

# Serve React frontend for all non-API routes
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Serve React frontend for all non-API routes"""
    # Don't interfere with API routes, health, docs, or static assets
    if (full_path.startswith("api/") or 
        full_path.startswith("health") or 
        full_path.startswith("docs") or
        full_path.startswith("assets/") or
        full_path.startswith("static/")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # For specific file extensions, try to serve from static directory first
    if "." in full_path and any(full_path.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.ico', '.svg']):
        static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    # Serve index.html for all frontend routes (React Router will handle routing)
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    index_file = os.path.join(static_dir, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        # Fallback API response if no frontend is built
        return {
            "message": "Indolent Forge API is running",
            "frontend": "not built - run 'npm run build' in frontend directory",
            "api_docs": "/docs",
            "requested_path": full_path
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the full error for debugging (server-side only)
    import traceback
    print(f"Internal server error: {str(exc)}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Return generic error to client (no sensitive information)
    error_response = {
        "error": "Internal server error", 
        "status_code": 500
    }
    
    # Only include debug info in development
    if settings.env == "development":
        error_response["debug"] = str(exc)
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )