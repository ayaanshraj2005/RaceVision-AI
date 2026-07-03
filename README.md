# RaceVision AI – Premium Motorsport Analytics & Machine Learning Platform

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**RaceVision AI** is a production-grade, end-to-end Machine Learning and predictive analytics platform for Formula-style motorsport racing. The project is designed to replicate real-world data science and software engineering workflows—implementing rigorous temporal data splitting, chronological feature engineering to eliminate forward-looking target leakage, model-agnostic permutation explainability (XAI), and a high-performance database-less FastAPI backend serving an interactive glassmorphic React (Vite) dashboard.

---

## Table of Contents
1. [Project Overview & Problem Statement](#project-overview--problem-statement)
2. [Platform Architecture](#platform-architecture)
3. [Repository Folder Structure](#repository-folder-structure)
4. [Data Science & Machine Learning Pipeline](#data-science--machine-learning-pipeline)
5. [FastAPI Backend APIs](#fastapi-backend-apis)
6. [React Analytics Dashboard](#react-analytics-dashboard)
7. [Installation & Local Setup](#installation--local-setup)
8. [License & Author](#license--author)

---

## Project Overview & Problem Statement

In professional motorsport (specifically Formula 1), race outcomes are dictated by a complex interplay of driver skill, vehicle aerodynamics, engine performance, starting position, and track-specific characteristics. Predicting classified finishing positions and podium probabilities is historically difficult due to:
1. **High Class Imbalance**: Podium finishes (P1, P2, P3) represent a minority class (~15% of grid entries).
2. **Qualifying Pace Dominance**: Starting grid slots determines up to 60% of race outcomes, but track layout properties (e.g. Monaco vs. Spa) dictate how strongly the starting slot is anchored.
3. **Temporal Dependency**: Driver form, team development scores, and familiarity change dynamically. Standard random K-Fold cross-validation introduces severe target leakage by shuffling past/future race logs.

### Solution Overview
RaceVision AI models this problem using a unified ML pipeline:
* **Chronological Split**: Trains on seasons 2010–2018, validates on 2019–2020, and tests on 2021 to ensure temporal stability.
* **Chronological Group-Shifting**: Rolling form and rates are calculated by sorting drivers and teams chronologically and shifting outcomes by 1 race (`shift(1)`) to predict *before the green light*.
* **Explainable AI (XAI)**: Demystifies predictions using model-agnostic Permutation Feature Importance and custom local contribution breakdowns.

---

## Platform Architecture

```mermaid
graph TD
    Client["Client (React App)"] -->|1. REST API Request| Main["src/main.py (FastAPI App)"]
    Main -->|2. Latency logging & CORS check| Middleware["RequestLoggingMiddleware"]
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

## Repository Folder Structure

```text
RaceVision AI/
 ├── data/
 │    ├── raw/                     # Original, immutable Formula 1 CSV files
 │    └── processed/               # Standardized, ML-ready processed datasets
 ├── models/                       # Serialized StandardScaler and trained Joblib models
 ├── reports/                      # Diagnostic and data audits markdown reports
 ├── src/                          # Backend source code module
 │    ├── api/routes/              # FastAPI route endpoints
 │    ├── config/                  # App configurations and system settings
 │    ├── middleware/              # Interceptor middlewares
 │    ├── pipelines/               # Data cleaning, EDA, FE, and training scripts
 │    ├── schemas/                 # Pydantic request/response validation schemas
 │    ├── services/                # Backend business services logic
 │    └── main.py                  # Web app launcher
 ├── frontend/                     # React (Vite) dashboard application
 │    ├── src/
 │    │    ├── layouts/            # Sidebar navigation shell layouts
 │    │    ├── pages/              # Overview, Drivers, Predictions, XAI panels
 │    │    ├── services/           # Axios service wrapper
 │    │    └── index.css           # Styling theme variables
 ├── tests/                        # Integration unit tests suite
 └── README.md                     # Portfolio overview documentation
```

---

## Data Science & Machine Learning Pipeline

### 1. Preprocessing & Cleaning
* Handle missing telemetry records appropriately using historical medians.
* Standardize column nomenclature and convert raw birth dates/stamps to active datetime objects.
* Isolate telemetry records from modern Hybrid/V8 seasons (2010–Present) to prevent zero-variance data leakage.

### 2. Feature Engineering Mappings
1. **`driver_recent_form`**: 5-race rolling average of finishing positions (`shift(1)`).
2. **`constructor_strength_index`**: Team's combined points sum over the last 3 races (`shift(1)`).
3. **`circuit_grid_importance`**: Track-specific Pearson correlation coefficient of grid-to-finish.
4. **`grid_delta_to_avg`**: Over/underperformance delta in qualifying (`grid` - `driver_rolling_grid`).
5. **`is_home_race`**: Binary flag indicating if driver nationality matches track country.

### 3. Model Training & Evaluation Metrics
We compared 5 regressors and 3 classifiers using GridSearchCV. Below are the final test outcomes:

#### Regression (Finishing Position)
| Algorithm | MAE | RMSE (Lower is Better) | R² Score |
| :--- | :---: | :---: | :---: |
| **Extra Trees** | **3.311** | **4.245** | **0.458** |
| Random Forest | 3.312 | 4.249 | 0.457 |
| Gradient Boosting | 3.434 | 4.318 | 0.439 |
| Linear Regression | 3.362 | 4.410 | 0.415 |

#### Classification (Podium Finish Chance)
| Algorithm | Accuracy | Precision | Recall | F1 Score (Higher is Better) | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Classifier** | **0.909** | **0.760** | **0.576** | **0.655** | **0.926** |
| Logistic Regression | 0.905 | 0.750 | 0.545 | 0.632 | 0.912 |
| Gradient Boosting | 0.898 | 0.733 | 0.500 | 0.595 | 0.922 |

---

## FastAPI Backend APIs

The backend exposes secure REST endpoints with strict Pydantic validation:

* **Predictions**:
  * `POST /predict/finish-position`: Predicts integer finishing position.
  * `POST /predict/podium-probability`: Predicts likelihood of P1–P3 finish (0.0 to 1.0).
  * `POST /predict/driver-performance`: Calculates qualifying and grid gain performance scores.
  * `POST /predict/team-performance`: Aggregates team strength indexes.
* **Explainable AI**:
  * `GET /explain/feature-importance`: Returns permutation feature weight statistics.
  * `POST /explain/prediction`: Explains forecasts using custom local contributions logic.
* **Analytics**:
  * `GET /analytics/dashboard`: Summary counts of races, circuits, top drivers.
  * `GET /analytics/drivers`: Driver profile standings and win counts.
  * `GET /analytics/teams`: Constructor stats and podium rates.
  * `GET /analytics/circuits`: Lists F1 circuits and Pearson correlation indexes.

---

## React Analytics Dashboard

The React frontend provides a dashboard styled with a dark theme and glassmorphism cards:
* **Interactive Predictions**: Enter qualifying grids and calculate predictions instantly using the backend ML models.
* **XAI Console**: Decode individual predictions into natural language.
* **Diagnostics Panel**: Embeds live learning curves, ROC curves, and residual charts.

---

## Installation & Local Setup

### 1. Prerequisites
Ensure you have python 3.10+ and Node.js v18+ installed on your local environment.

### 2. Backend Installation & Run
1. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the FastAPI server:
   ```bash
   python -m uvicorn src.main:app --reload --port 8000
   ```
3. Interactive Swagger documentation is now available at `http://localhost:8000/docs`.

### 3. Frontend Installation & Run
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the React dashboard at `http://localhost:5173`.

---

## License & Author
This project is licensed under the MIT License. Developed by **Ayaansh Raj** as a premium portfolio showcase demonstrating data science, machine learning, software architecture, and full-stack API integration.
