from fastapi import APIRouter, Depends, HTTPException
from src.schemas.prediction import (
    PredictionRequest, FinishPositionResponse, 
    PodiumProbabilityResponse, DriverPerformanceResponse, 
    TeamPerformanceResponse
)
from src.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["Predictions"])

# Reusable service instance
_prediction_service = None

def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        try:
            _prediction_service = PredictionService()
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return _prediction_service

@router.post("/finish-position", response_model=FinishPositionResponse, summary="Predict driver finishing positions")
def predict_finish_position(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    """
    Predicts the raw model regression score and maps it to a unique, dense integer classified finishing rank (P1-P20) for all drivers.
    """
    entries_dict = [entry.model_dump() for entry in request.entries]
    try:
        preds = service.predict_finish_position(entries_dict)
        return {"race_id": request.race_id, "predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/podium-probability", response_model=PodiumProbabilityResponse, summary="Predict driver podium probabilities")
def predict_podium_probability(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    """
    Predicts the binary probability (0.0 to 1.0) of each driver finishing in a podium position (P1, P2, or P3).
    """
    entries_dict = [entry.model_dump() for entry in request.entries]
    try:
        preds = service.predict_podium_probability(entries_dict)
        return {"race_id": request.race_id, "predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/driver-performance", response_model=DriverPerformanceResponse, summary="Predict driver performance scores")
def predict_driver_performance(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    """
    Generates a performance index score (0-100) indicating qualifying pace efficiency and grid-gain performance.
    """
    entries_dict = [entry.model_dump() for entry in request.entries]
    try:
        preds = service.predict_driver_performance(entries_dict)
        return {"race_id": request.race_id, "predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/team-performance", response_model=TeamPerformanceResponse, summary="Predict constructor performance index")
def predict_team_performance(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    """
    Computes an aggregated constructor performance score (0-100) representing the team's combined vehicle race pace output.
    """
    entries_dict = [entry.model_dump() for entry in request.entries]
    try:
        preds = service.predict_team_performance(entries_dict)
        return {"race_id": request.race_id, "predictions": preds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
