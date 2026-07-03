# Backend Architecture & API Documentation – RaceVision AI

This document details the production-ready FastAPI backend architecture, API schemas, routes, middleware, request/response examples, and a Mermaid dataflow diagram.

---

## 1. Directory Structure

The backend follows clean, modular software engineering architecture, isolating routes, Pydantic schemas, business services, and system configs:

```text
src/
 ├── api/
 │    └── routes/
 │         ├── prediction.py       # Predict finishing ranks, podium probability, indexes
 │         ├── analytics.py        # Database-less historical motorsport statistics
 │         ├── explain.py          # Model parameters, features, and local explainability
 │         └── health.py           # Standard health checking and versioning
 ├── config/
 │    └── settings.py              # Base paths configurations
 ├── middleware/
 │    └── logging_middleware.py    # Request interceptor measuring latency
 ├── schemas/
 │    ├── prediction.py            # Pydantic schemas validating prediction structures
 │    ├── analytics.py             # Pydantic schemas validating analytics structures
 │    └── explain.py               # Pydantic schemas validating XAI structures
 ├── services/
 │    ├── prediction_service.py    # Encapsulates joblib inference executions
 │    └── analytics_service.py     # Parses processed datasets with fast lookups
 └── main.py                       # Application assembly and CORS config
```

---

## 2. Backend Dataflow Diagram

The following Mermaid diagram outlines how client requests flow through the backend layers:

```mermaid
graph TD
    Client["Client (React App / HTTP Client)"] -->|1. REST API Request| Main["src/main.py (FastAPI App)"]
    Main -->|2. latency logs & CORS check| Middleware["RequestLoggingMiddleware"]
    Main -->|3. Route Resolving| Routes["src/api/routes/*.py"]
    Routes -->|4. Input Parsing & Validation| Schemas["src/schemas/*.py (Pydantic Models)"]
    Routes -->|5. Calls Business Logic| Services["src/services/*.py"]
    Services -->|6a. ML Inference (scaler & models)| Joblib["models/*.joblib (Serialized Objects)"]
    Services -->|6b. CSV Data Queries| CSVs["data/processed/*.csv (F1 Clean Data)"]
    Services -->|7. Return Results| Routes
    Routes -->|8. Validate Response Schema| Schemas
    Routes -->|9. JSON Response| Client
```

---

## 3. API Reference & Examples

### A. Health & Version APIs
* **`GET /health`**
  * *Response Example:*
    ```json
    {
      "status": "healthy",
      "service": "RaceVision AI Backend"
    }
    ```
* **`GET /version`**
  * *Response Example:*
    ```json
    {
      "version": "1.0.0",
      "api_standard": "REST",
      "author": "RaceVision AI Data Science Team"
    }
    ```

---

### B. Machine Learning Prediction APIs
All prediction endpoints accept a standard `PredictionRequest` payload representing the race weekend grid and entries.

* **`POST /predict/finish-position`**
  * *Request Example:*
    ```json
    {
      "race_id": 1051,
      "entries": [
        {
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
      ]
    }
    ```
  * *Response Example:*
    ```json
    {
      "race_id": 1051,
      "predictions": [
        {
          "driver_id": 1,
          "driver_name": "Lewis Hamilton",
          "predicted_raw_score": 1.25,
          "predicted_finishing_position": 1
        }
      ]
    }
    ```

* **`POST /predict/podium-probability`**
  * *Response Example:*
    ```json
    {
      "race_id": 1051,
      "predictions": [
        {
          "driver_id": 1,
          "driver_name": "Lewis Hamilton",
          "predicted_podium_probability": 0.615
        }
      ]
    }
    ```

---

### C. Explainable AI (XAI) APIs
* **`POST /explain/prediction`**
  * *Request Example:*
    ```json
    {
      "driver_name": "Lewis Hamilton",
      "constructor_name": "Mercedes",
      "grid": 1,
      "driver_recent_form": 2.2,
      "constructor_strength_index": 39.7,
      "grid_delta_to_avg": -0.8,
      "circuit_grid_importance": 0.60,
      "circuit_name": "Monaco GP"
    }
    ```
  * *Response Example:*
    ```json
    {
      "driver_name": "Lewis Hamilton",
      "predicted_finishing_position": 1,
      "predicted_podium_probability": 0.615,
      "explanation": "Driver Lewis Hamilton is predicted to finish in Position 1 (Podium Probability: 61.5%) because:\n- Strong qualifying pace starting from Grid position P1\n- High-performance vehicle package from Mercedes (Recent Team score: 39.7)\n- Strong current driver form (Recent average finish: 2.2)\n- High track layout grid advantage at Monaco GP (Pearson: 0.60)"
    }
    ```

---

## 4. Backend Deployment Readiness Checklist
- [x] **Model Objects Serialized**: Loaded and validated from `/models/`.
- [x] **Pydantic Schemas Configured**: Both requests and responses strictly validated.
- [x] **CORS Enabled**: Origin access `*` allows frontend integrations.
- [x] **Global Validation Failures (HTTP 422) Handled**: Informative schemas error output returned.
- [x] **Global System Errors (HTTP 500) Handled**: Prevents raw backend stack trace leakage.
- [x] **Automated APIs Test Coverage**: 16/16 unittest validations passed successfully.
- [x] **latency logging middleware mounted**: Prints processing times for debugging.
