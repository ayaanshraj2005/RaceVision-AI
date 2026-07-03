from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import logging

from src.middleware.logging_middleware import RequestLoggingMiddleware
from src.api.routes import prediction, analytics, explain, health

# Configure main app logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RaceVisionMain")

# Swagger Docs Metadata configuration
app = FastAPI(
    title="RaceVision AI Analytics Platform API",
    description=(
        "Production-ready backend APIs serving machine learning predictive analytics, "
        "Explainable AI (XAI) transparent summaries, and motorsport historical datasets for F1.\n\n"
        "**Features Include:**\n"
        "- Driver finishing positions predictions with unique classification ranks (Extra Trees Regressor)\n"
        "- Podium finish likelihood probabilities (Random Forest Classifier)\n"
        "- Driver/Constructor performance scores index computation\n"
        "- Granular analytics queries on historical datasets (drivers, constructors, circuits, seasons)\n"
        "- Transparent prediction explainability (local explanations and permutation metrics)"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Policy configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Global Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation failure on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request ValidationError",
            "message": "Invalid request fields. Please review parameters schema requirements.",
            "details": exc.errors()
        }
    )

# Global General Exception Handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during execution. Contact database administrator."
        }
    )

# Register Routers
app.include_router(prediction.router)
app.include_router(analytics.router)
app.include_router(explain.router)
app.include_router(health.router)

app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")

@app.on_event("startup")
def startup_event():
    logger.info("RaceVision AI FastAPI backend services started successfully.")
