"""
Capitol Engineering Company - Simple FastAPI Server
Minimal server for testing basic functionality
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title="Capitol Takeoff API - Test Server",
    version="1.0.0",
    description="Professional Takeoff System API - Capitol Engineering Company"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Capitol Takeoff API",
        "version": "1.0.0",
        "company": "Capitol Engineering Company",
        "status": "running",
        "database": "postgresql://localhost:5432/capitol_takeoff",
        "message": "Capitol Engineering Professional Steel Estimating System"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Capitol Takeoff API",
        "company": "Capitol Engineering Company",
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint for API functionality"""
    return {
        "message": "Capitol Takeoff API is working",
        "company": "Capitol Engineering Company",
        "features": [
            "Material Database Management",
            "11-Column Takeoff System", 
            "Real-time Calculations",
            "Project Management",
            "AI-Enhanced Proposals"
        ]
    }

@app.get("/api/v1/company")
async def company_info():
    """Company information endpoint"""
    return {
        "company_name": "Capitol Engineering Company",
        "address": "724 E Southern Pacific Dr, Phoenix AZ 85034",
        "phone": "602-281-6517",
        "mobile": "951-732-1514",
        "website": "www.capitolaz.com",
        "services": [
            "Steel Fabrication",
            "Professional Takeoffs",
            "Project Estimation",
            "AISC Certified"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)