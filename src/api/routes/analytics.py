from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.schemas.analytics import DashboardStats, DriverAnalytics, TeamAnalytics, CircuitAnalytics, SeasonSummary
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

_analytics_service = None

def get_analytics_service() -> AnalyticsService:
    global _analytics_service
    if _analytics_service is None:
        try:
            _analytics_service = AnalyticsService()
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))
    return _analytics_service

@router.get("/dashboard", response_model=DashboardStats, summary="Fetch general dashboard summary statistics")
def get_dashboard(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/drivers", response_model=List[DriverAnalytics], summary="List all drivers and career win stats")
def get_drivers(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_drivers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/drivers/{driver_id}", response_model=DriverAnalytics, summary="Get details for a single driver")
def get_driver_by_id(driver_id: int, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        data = service.get_driver_by_id(driver_id)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Driver with ID {driver_id} not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/teams", response_model=List[TeamAnalytics], summary="List all constructors and career wins")
def get_teams(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_teams()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/teams/{team_id}", response_model=TeamAnalytics, summary="Get details for a single team")
def get_team_by_id(team_id: int, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        data = service.get_team_by_id(team_id)
        if data is None:
            raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/circuits", response_model=List[CircuitAnalytics], summary="List Grand Prix circuits and grid importance weights")
def get_circuits(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_circuits()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")

@router.get("/seasons", response_model=List[SeasonSummary], summary="Fetch historical seasons champion drivers and constructors")
def get_seasons(service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_seasons()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database lookup error: {str(e)}")
