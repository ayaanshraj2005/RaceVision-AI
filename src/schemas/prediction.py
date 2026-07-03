from pydantic import BaseModel, Field
from typing import List

class DriverRaceEntry(BaseModel):
    driver_id: int
    driver_name: str
    constructor_id: int
    constructor_name: str
    grid: int = Field(..., ge=1, le=24, description="Starting grid position")
    driver_age: float = Field(..., description="Driver age in years")
    driver_experience: int = Field(..., description="Number of race starts")
    driver_recent_form: float = Field(..., description="5-race rolling finish position average")
    driver_rolling_grid: float = Field(..., description="5-race rolling grid average")
    driver_avg_finish: float = Field(..., description="Career average finish order")
    driver_consistency: float = Field(..., description="Career finish position std dev")
    driver_win_rate: float = Field(..., description="Career win percentage")
    driver_podium_rate: float = Field(..., description="Career podium percentage")
    driver_top10_rate: float = Field(..., description="Career top 10 percentage")
    driver_dnf_rate: float = Field(..., description="Career DNF rate")
    grid_delta_to_avg: float = Field(..., description="Current grid minus rolling average grid")
    constructor_strength_index: float = Field(..., description="Rolling average of constructor team points")
    circuit_familiarity: int = Field(..., description="Starts at this track")
    circuit_grid_importance: float = Field(..., description="Track grid-to-finish Pearson correlation")
    is_home_race: int = Field(..., ge=0, le=1, description="Binary home race indicator")

    model_config = {
        "json_schema_extra": {
            "example": {
                "driver_id": 1,
                "driver_name": "Lewis Hamilton",
                "constructor_id": 131,
                "constructor_name": "Mercedes",
                "grid": 1,
                "driver_age": 36.2,
                "driver_experience": 266,
                "driver_recent_form": 2.2,
                "driver_rolling_grid": 1.8,
                "driver_avg_finish": 3.4,
                "driver_consistency": 4.1,
                "driver_win_rate": 0.35,
                "driver_podium_rate": 0.61,
                "driver_top10_rate": 0.88,
                "driver_dnf_rate": 0.08,
                "grid_delta_to_avg": -0.8,
                "constructor_strength_index": 39.7,
                "circuit_familiarity": 14,
                "circuit_grid_importance": 0.60,
                "is_home_race": 0
            }
        }
    }

class PredictionRequest(BaseModel):
    race_id: int = Field(..., description="Unique Race ID reference")
    entries: List[DriverRaceEntry] = Field(..., min_length=1, description="List of driver weekend entries")

class FinishPositionPrediction(BaseModel):
    driver_id: int
    driver_name: str
    predicted_raw_score: float
    predicted_finishing_position: int

class FinishPositionResponse(BaseModel):
    race_id: int
    predictions: List[FinishPositionPrediction]

class PodiumProbabilityPrediction(BaseModel):
    driver_id: int
    driver_name: str
    predicted_podium_probability: float

class PodiumProbabilityResponse(BaseModel):
    race_id: int
    predictions: List[PodiumProbabilityPrediction]

class DriverPerformancePrediction(BaseModel):
    driver_id: int
    driver_name: str
    driver_performance_score: int

class DriverPerformanceResponse(BaseModel):
    race_id: int
    predictions: List[DriverPerformancePrediction]

class TeamPerformancePrediction(BaseModel):
    constructor_id: int
    constructor_name: str
    team_performance_score: int

class TeamPerformanceResponse(BaseModel):
    race_id: int
    predictions: List[TeamPerformancePrediction]
