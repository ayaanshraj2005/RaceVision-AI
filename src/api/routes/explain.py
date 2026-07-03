from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from src.schemas.explain import (
    FeatureImportanceResponse, ExplainPredictionRequest, 
    ExplainPredictionResponse, ModelMetricsResponse, ModelInformationResponse,
    DriverDetailResponse
)
from src.services.prediction_service import PredictionService
import numpy as np

router = APIRouter(tags=["Model Explainability"])

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

@router.get("/drivers", response_model=List[str], summary="List unique driver names available in dataset")
def list_drivers(season: Optional[int] = None, service: PredictionService = Depends(get_prediction_service)):
    try:
        return service.get_drivers_list(season)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drivers/{driver_name}", response_model=DriverDetailResponse, summary="Get details and team mapping for a driver")
def get_driver_details(driver_name: str, season: Optional[int] = None, service: PredictionService = Depends(get_prediction_service)):
    details = service.get_driver_details(driver_name, season)
    if not details:
        raise HTTPException(status_code=404, detail=f"Driver '{driver_name}' not found in database for the selected season.")
    return details

@router.get("/explain/feature-importance", response_model=FeatureImportanceResponse, summary="Get global feature importance weights")
def get_feature_importances(service: PredictionService = Depends(get_prediction_service)):
    """
    Returns the global feature importance weights of the best regressor (Extra Trees)
    and the model-agnostic Permutation Importance values.
    """
    # Relative weights from our best model runs
    global_importance = {
        "grid": 0.654,
        "constructor_strength_index": 0.125,
        "driver_recent_form": 0.082,
        "driver_avg_finish": 0.045,
        "driver_rolling_grid": 0.031,
        "grid_delta_to_avg": 0.021,
        "driver_experience": 0.015,
        "driver_podium_rate": 0.012,
        "driver_age": 0.008,
        "circuit_grid_importance": 0.005,
        "circuit_familiarity": 0.002,
        "is_home_race": 0.000,
        "driver_consistency": 0.000,
        "driver_win_rate": 0.000,
        "driver_top10_rate": 0.000,
        "driver_dnf_rate": 0.000
    }
    
    permutation_importance = {
        "grid": 0.384,
        "driver_rolling_grid": 0.052,
        "grid_delta_to_avg": 0.041,
        "constructor_strength_index": 0.038,
        "driver_recent_form": 0.021,
        "driver_avg_finish": 0.012,
        "driver_podium_rate": 0.009,
        "driver_experience": 0.005,
        "driver_age": 0.004,
        "circuit_grid_importance": 0.002,
        "circuit_familiarity": 0.001,
        "is_home_race": 0.000,
        "driver_consistency": 0.000,
        "driver_win_rate": 0.000,
        "driver_top10_rate": 0.000,
        "driver_dnf_rate": 0.000
    }
    return {
        "feature_importance": global_importance,
        "permutation_importance": permutation_importance
    }

@router.post("/explain/prediction", response_model=ExplainPredictionResponse, summary="Explain individual driver predictions")
def explain_prediction(request: ExplainPredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    """
    Accepts driver telemetry configurations, standardizes them, runs the ML classifiers/regressors,
    and returns a transparent human-readable explanation of why the driver is forecast for that position.
    """
    # Validate driver-constructor alignment
    is_valid, err_msg = service.validate_driver_constructor_season(request.driver_name, request.constructor_name, request.season)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)

    try:
        # Look up actual telemetry parameters from dataset for this driver/season to avoid hardcoded defaults
        details = service.get_driver_details(request.driver_name, request.season)
        if details:
            driver_age = details.get("age", 28.5)
            driver_experience = details.get("experience", 120)
            driver_rolling_grid = details.get("rolling_grid", request.grid + 0.5)
            driver_avg_finish = details.get("avg_finish", request.driver_recent_form + 1.0)
            driver_consistency = details.get("consistency", 4.5)
            driver_win_rate = details.get("historical_win_rate", 0.05)
            driver_podium_rate = details.get("podium_rate", 0.15)
            driver_top10_rate = details.get("top10_rate", 0.55)
            driver_dnf_rate = details.get("dnf_rate", 0.12)
            circuit_familiarity = details.get("circuit_familiarity", 6)
        else:
            driver_age = 28.5
            driver_experience = 120
            driver_rolling_grid = request.grid + 0.5
            driver_avg_finish = request.driver_recent_form + 1.0
            driver_consistency = 4.5
            driver_win_rate = 0.05
            driver_podium_rate = 0.15
            driver_top10_rate = 0.55
            driver_dnf_rate = 0.12
            circuit_familiarity = 6

        # Build complete feature dictionary
        full_entry = {
            "driver_id": 999,
            "driver_name": request.driver_name,
            "constructor_id": 999,
            "constructor_name": request.constructor_name,
            "grid": request.grid,
            "driver_age": driver_age,
            "driver_experience": driver_experience,
            "driver_recent_form": request.driver_recent_form,
            "driver_rolling_grid": driver_rolling_grid,
            "driver_avg_finish": driver_avg_finish,
            "driver_consistency": driver_consistency,
            "driver_win_rate": driver_win_rate,
            "driver_podium_rate": driver_podium_rate,
            "driver_top10_rate": driver_top10_rate,
            "driver_dnf_rate": driver_dnf_rate,
            "grid_delta_to_avg": request.grid_delta_to_avg,
            "constructor_strength_index": request.constructor_strength_index,
            "circuit_familiarity": circuit_familiarity if details else 6,
            "circuit_grid_importance": request.circuit_grid_importance,
            "is_home_race": 0
        }
        
        # Call explain_prediction_local
        explain_res = service.explain_prediction_local(full_entry)
        
        # Predict
        preds_list = service.predict_finish_position([full_entry])
        probs_list = service.predict_podium_probability([full_entry])
        
        predicted_pos = int(preds_list[0]["predicted_finishing_position"])
        podium_prob = float(probs_list[0]["predicted_podium_probability"])
        
        return {
            "driver_name": request.driver_name,
            "predicted_finishing_position": predicted_pos,
            "predicted_podium_probability": podium_prob,
            "explanation": explain_res["explanation"],
            "confidence_score": explain_res["confidence_score"],
            "top_positive_factors": explain_res["top_positive_factors"],
            "top_negative_factors": explain_res["top_negative_factors"],
            "local_contributions": explain_res["local_contributions"],
            "radar_metrics": explain_res["radar_metrics"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explainability execution error: {str(e)}")

@router.get("/model/metrics", response_model=ModelMetricsResponse, summary="Get frozen model performance evaluations")
def get_model_metrics():
    """
    Returns frozen evaluation metrics on the Test Set (2021 season) from our model evaluation reports.
    """
    regression = {
        "MAE": 3.311,
        "MSE": 18.022,
        "RMSE": 4.245,
        "R2": 0.458
    }
    classification = {
        "Accuracy": 0.909,
        "Precision": 0.760,
        "Recall": 0.576,
        "F1": 0.655,
        "ROC-AUC": 0.926
    }
    return {
        "regression_metrics": regression,
        "classification_metrics": classification
    }

@router.get("/model/information", response_model=ModelInformationResponse, summary="Get model architectural configurations")
def get_model_info(service: PredictionService = Depends(get_prediction_service)):
    """
    Returns architecture configurations including classifier/regressor type names and features used.
    """
    return {
        "regressor_algorithm": type(service.reg_model).__name__,
        "classifier_algorithm": type(service.clf_model).__name__,
        "training_data_rows": 3877,
        "features_used": service.features,
        "split_strategy": "Chronological Split (Train: seasons 2010-2018, Val: seasons 2019-2020, Test: season 2021)"
    }
