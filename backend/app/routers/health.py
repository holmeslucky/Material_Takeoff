from fastapi import APIRouter

router = APIRouter()

@router.get("/live")
def live():
    """Kubernetes liveness probe"""
    return {"ok": True}

@router.get("/ready")
def ready():
    """Kubernetes readiness probe"""
    # TODO: Add database connectivity check
    return {"ok": True}

@router.get("/version")
def version():
    """API version info"""
    return {
        "name": "Capitol Takeoff API",
        "version": "0.1.0",
        "environment": "development"
    }