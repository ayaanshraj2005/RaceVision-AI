# ==========================================
# Startup Script - RaceVision AI Backend
# ==========================================

Write-Host "Initializing RaceVision AI FastAPI Server..." -ForegroundColor Green
python -m uvicorn src.main:app --reload --port 8000
