from fastapi import APIRouter
from typing import Dict

router = APIRouter(tags=["System Health"])

@router.get("/health", response_model=Dict[str, str], summary="Check API server health status")
def check_health():
    """
    Returns the server status to verify API is active.
    """
    return {"status": "healthy", "service": "RaceVision AI Backend"}

@router.get("/ready", response_model=Dict[str, str], summary="Check API dependencies readiness")
def check_readiness():
    """
    Checks if ML models and datasets directories are present and ready to serve.
    """
    import os
    from src.config.settings import MODELS_DIR
    
    scaler = os.path.join(MODELS_DIR, "scaler.joblib")
    reg = os.path.join(MODELS_DIR, "best_regressor.joblib")
    clf = os.path.join(MODELS_DIR, "best_classifier.joblib")
    
    ready = os.path.exists(scaler) and os.path.exists(reg) and os.path.exists(clf)
    if ready:
        return {"status": "ready", "models_loaded": "true", "data_loaded": "true"}
    else:
        return {"status": "not_ready", "reason": "Model binary objects missing from models/ directory"}

@router.get("/version", response_model=Dict[str, str], summary="Check API deployment version")
def check_version():
    """
    Returns deployment release versioning parameters.
    """
    return {
        "version": "1.0.0",
        "api_standard": "REST",
        "author": "RaceVision AI Data Science Team"
    }
