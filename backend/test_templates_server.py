#!/usr/bin/env python3
"""
Minimal test server to verify templates API is working
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
app = FastAPI(title="Templates Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include only the templates router
from app.api.v1.templates import router as templates_router
app.include_router(templates_router, prefix="/api/v1/templates", tags=["templates"])

# Test endpoint
@app.get("/")
def root():
    return {"message": "Templates test server is running"}

@app.get("/test")
def test():
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7000)