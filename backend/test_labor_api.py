"""
Simple test server to verify labor API endpoints work
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.labor import router as labor_router

# Create simple FastAPI app just for labor testing
app = FastAPI(title="Labor API Test", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the labor router
app.include_router(labor_router, prefix="/api/v1/labor", tags=["labor"])

@app.get("/")
def root():
    return {"status": "Labor API test server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)