from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class FeatureImportanceResponse(BaseModel):
    feature_importance: Dict[str, float] = Field(..., description="Tree splits relative importance values")
    permutation_importance: Dict[str, float] = Field(..., description="Permutation accuracy decrease on test set")

class ExplainPredictionRequest(BaseModel):
    driver_name: str = Field(..., description="Driver full name")
    constructor_name: str = Field(..., description="Constructor/Team name")
    grid: int = Field(..., ge=1, le=24, description="Starting grid position")
    driver_recent_form: float = Field(..., description="5-race average finishing position")
    constructor_strength_index: float = Field(..., description="Team recent points index")
    grid_delta_to_avg: float = Field(..., description="Grid minus rolling average grid")
    circuit_grid_importance: float = Field(..., description="Track grid-to-finish correlation score")
    circuit_name: str = Field(..., description="Grand Prix circuit name")
    season: Optional[int] = Field(None, description="F1 season/year")

    model_config = {
        "json_schema_extra": {
            "example": {
                "driver_name": "Lewis Hamilton",
                "constructor_name": "Mercedes",
                "grid": 1,
                "driver_recent_form": 2.2,
                "constructor_strength_index": 39.7,
                "grid_delta_to_avg": -0.8,
                "circuit_grid_importance": 0.60,
                "circuit_name": "Monaco GP",
                "season": 2021
            }
        }
    }

class DriverDetailResponse(BaseModel):
    driver: str
    team: str
    recent_form: float
    team_strength: float
    experience: int
    constructor_strength: float
    historical_win_rate: float
    age: float
    rolling_grid: float
    avg_finish: float
    consistency: float
    podium_rate: float
    top10_rate: float
    dnf_rate: float
    grid_delta_to_avg: float
    season: int

class ExplainPredictionResponse(BaseModel):
    driver_name: str
    predicted_finishing_position: int
    predicted_podium_probability: float
    explanation: str
    confidence_score: Optional[float] = None
    top_positive_factors: Optional[List[str]] = None
    top_negative_factors: Optional[List[str]] = None
    local_contributions: Optional[Dict[str, float]] = None
    radar_metrics: Optional[Dict[str, float]] = None

class ModelMetricsResponse(BaseModel):
    regression_metrics: Dict[str, float]
    classification_metrics: Dict[str, float]

class ModelInformationResponse(BaseModel):
    regressor_algorithm: str
    classifier_algorithm: str
    training_data_rows: int
    features_used: List[str]
    split_strategy: str

