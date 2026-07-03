# Feature Engineering Report – RaceVision AI

This document details the feature engineering pipeline, chronological shift logic to prevent target leakage, multicollinearity diagnostics, and the final feature selection roadmap for model training.

---

## 1. Newly Engineered Features

The following features were created using chronological group-shift operations on the cleaned F1 datasets:

| Feature Name | Type | Formula / Origin | EDA Insights Supported | ML Impact |
| :--- | :--- | :--- | :--- | :--- |
| **`driver_age`** | Numeric | `race_timestamp - dob` | Driver experience changes over time. | Captures driver maturity and aging performance curves. |
| **`driver_experience`** | Numeric | Cumulative race count | Historical driver capability. | Proxy for racecraft, track familiarity, and DNF avoidance. |
| **`driver_recent_form`** | Numeric | 5-race rolling average of `position_order` (shifted) | Driver consistency profiles. | Captures driver form momentum independent of vehicle package. |
| **`driver_rolling_grid`** | Numeric | 5-race rolling average of `grid` (shifted) | Grid position is the anchor predictor. | Represents qualifying form over recent Grand Prix. |
| **`driver_avg_finish`** | Numeric | Cumulative career average of `position_order` (shifted) | Long-term performance levels. | Base rating proxy for absolute driver strength. |
| **`driver_consistency`** | Numeric | Cumulative career standard deviation of `position_order` (shifted) | Driver variance boxes. | Highlights DNF-prone or erratic drivers versus consistent finishers. |
| **`driver_win_rate`** | Numeric | Cumulative wins / career entries (shifted) | Win distribution charts. | Provides the model with win-specific career probability scales. |
| **`driver_podium_rate`** | Numeric | Cumulative podiums / career entries (shifted) | Podium distribution charts. | Directly anchors target classifications. |
| **`driver_top10_rate`** | Numeric | Cumulative top 10s / career entries (shifted) | Uniformity of points classifications. | Base probability score for top 10 classification. |
| **`driver_dnf_rate`** | Numeric | Cumulative DNFs / career entries (shifted) | DNF imbalance (73% historical DNFs). | Predicts probability of mechanical or collision retirement. |
| **`grid_delta_to_avg`** | Numeric | `grid` - `driver_rolling_grid` | Qualifying pace variance. | Captures qualifying over/underperformance in the current race. |
| **`constructor_strength`** | Numeric | Team's joint points over last 3 races (shifted) | Team podium dominance (80% of performance). | Embedded representation of car aerodynamic/engine pace. |
| **`circuit_familiarity`** | Numeric | Expanding count of driver starts at circuit | Experience curve analysis. | Accounts for driver experience at complex layouts (e.g. Spa, Monaco). |
| **`is_home_race`** | Binary | `driver_nationality` matches `circuit_country` | Home race support. | Capture structural motivation / home-field familiarity. |
| **`circuit_grid_importance`** | Numeric | Global Pearson correlation of grid-to-finish per track | Monaco ($r\approx 0.60$) vs. Spa ($r\approx 0.38$). | Circuit grid interaction term, dynamically weighting grid starts. |

---

## 2. Preventing Target Leakage: The Group-Shift Principle

> [!IMPORTANT]
> **No Forward Looking Bias**: In standard F1 datasets, features like `driver_recent_form` (rolling finishing position) can cause severe target leakage if they include the current race's finishing position.
> 
> * **Shift Mechanism**: Before running rolling or expanding averages, the results are sorted chronologically per driver and constructor and shifted by 1 race (`shift(1)`).
> * **Result**: The rolling features at race $N$ are calculated using only data from races $1$ to $N-1$, ensuring the model trains on information available *before the green light*.

---

## 3. Multicollinearity (VIF) Diagnostic Report

Multicollinearity occurs when predictors are highly correlated, causing coefficients to inflate and creating model instability in linear/logistic regression.

### VIF Summary Table
| Rank | Feature Name | VIF Score | Status / Recommendation |
| :---: | :--- | :---: | :--- |
| 1 | `grid` | 127.05 | HIGH (collinear) |
| 5 | `driver_rolling_grid` | 94.40 | HIGH (collinear) |
| 12 | `grid_delta_to_avg` | 56.18 | HIGH (collinear) |
| 6 | `driver_avg_finish` | 24.27 | HIGH (collinear) |
| 10 | `driver_top10_rate` | 15.04 | HIGH (collinear) |
| 9 | `driver_podium_rate` | 13.96 | HIGH (collinear) |
| 3 | `driver_experience` | 8.63 | Optimal |
| 8 | `driver_win_rate` | 7.81 | Optimal |
| 11 | `driver_dnf_rate` | 5.86 | Optimal |
| 4 | `driver_recent_form` | 5.28 | Optimal |
| 2 | `driver_age` | 5.05 | Optimal |
| 13 | `constructor_strength_index` | 3.77 | Optimal |
| 7 | `driver_consistency` | 3.12 | Optimal |
| 14 | `circuit_familiarity` | 2.65 | Optimal |
| 15 | `circuit_grid_importance` | 1.05 | Optimal |
| 16 | `is_home_race` | 1.01 | Optimal |

### Highly Collinear Features (VIF > 10)
> [!WARNING]
> The following features have VIF scores exceeding 10, indicating highly redundant signals:
> * `grid, driver_rolling_grid, grid_delta_to_avg, driver_avg_finish, driver_top10_rate, driver_podium_rate`
>
> **Recommendations for Phase 5 (Modeling)**:
> 1. For **Linear/Logistic models**, remove `driver_avg_finish` and `driver_podium_rate` to prevent multicollinearity coefficients inflation.
> 2. For **Tree-based models (Random Forest, XGBoost)**, VIF collinearity does not impact model convergence or split accuracy. It is safe to retain these features as they help define multiple branching criteria.

---

## 4. Target Leakage Columns Removed
The following columns were dropped from the training set as they contain post-race targets:
`position`, `position_text`, `points`, `milliseconds`, `time`, `fastest_lap_time`, `fastest_lap_time_seconds`, `fastest_lap_speed`, `rank`, `fastest_lap`

---

## 5. Summary of ML Readiness
* **Master Dataset Size**: `5,097` rows and `27` columns.
* **Modern Scope**: Subsetted to seasons **2010–Present** to ensure complete qualifying telemetry (Q1/Q2/Q3) and avoid zero-variance columns in older eras.
* **Storage**: Saved to `data/processed/ml_ready_dataset.csv`.
