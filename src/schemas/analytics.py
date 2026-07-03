from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DashboardStats(BaseModel):
    total_races: int
    total_drivers: int
    total_constructors: int
    total_circuits: int
    seasons_covered: List[int]
    top_drivers_by_wins: List[Dict[str, Any]]
    top_teams_by_wins: List[Dict[str, Any]]

class DriverAnalytics(BaseModel):
    driver_id: int
    driver_name: str
    nationality: str
    code: Optional[str] = None
    dob: str
    wins: int
    podiums: int
    total_races: int

class TeamAnalytics(BaseModel):
    constructor_id: int
    constructor_name: str
    nationality: str
    wins: int
    podiums: int
    total_races: int

class CircuitAnalytics(BaseModel):
    circuit_id: int
    circuit_name: str
    location: str
    country: str
    total_races: int
    grid_importance_correlation: float

class SeasonSummary(BaseModel):
    year: int
    total_races: int
    champion_driver: Optional[str] = None
    champion_constructor: Optional[str] = None
