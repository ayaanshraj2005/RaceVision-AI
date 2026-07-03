# Technical & Behavioral Interview Preparation Guide – RaceVision AI

This guide contains 50 Technical Questions and 50 HR/Behavioral Questions, specifically tailored for **RaceVision AI**, designed to prep you for Data Scientist, Machine Learning Engineer, Python Developer, and Software Architect interviews.

---

## Part 1: Technical Questions (50 Q&As)

### A. Data Science & Machine Learning Pipeline (15 Q&As)

#### Q1: Why did you choose a chronological split instead of a random train-test split?
**Answer**: Formula 1 is a sequential time-series event where driver aging, track experience, and team development evolve chronologically. A random train-test split shuffles future races into the training set, causing **forward-looking target leakage** and artificially inflating test accuracy. We used 2010–2018 for training, 2019–2020 for validation, and 2021 for testing.

#### Q2: What is target leakage, and how did you prevent it during feature engineering?
**Answer**: Target leakage occurs when features containing information about the future target (`position_order` or `is_podium` in this race) are included in the predictors. To prevent this, we grouped data by `driver_id` and `constructor_id`, sorted chronologically, and shifted target variables by 1 race (`shift(1)`) *before* computing rolling/expanding averages.

#### Q3: Why did you choose Extra Trees Regressor over standard Decision Trees or Random Forest?
**Answer**: Random Forest searches for the optimal split node among a random subset of features. Extra Trees (Extremely Randomized Trees) takes this step further by choosing split values completely *randomly* for each feature rather than searching for the best split threshold. This adds regularization, decreases variance, reduces overfitting on F1's noisy finishing positions, and yields the lowest test RMSE (4.245).

#### Q4: How did you handle class imbalance in podium probability prediction?
**Answer**: Podium finishes (P1, P2, P3) represent only ~15% of grid entries. Standard accuracy is misleading here since a model predicting "no podium" for everyone would achieve ~85% accuracy. We optimized the **F1 Score** (which balances Precision and Recall) and used a **Random Forest Classifier** which handles sparse classes robustly, yielding a Test F1 of 0.655 and ROC-AUC of 0.926.

#### Q5: What is the Variance Inflation Factor (VIF), and why did qualifying features show high VIF scores?
**Answer**: VIF measures multicollinearity among predictors. We found `grid` (VIF: 127.05), `driver_rolling_grid` (VIF: 94.40), and `grid_delta_to_avg` (VIF: 56.17) had extremely high scores. This is due to a direct linear combination: `grid_delta_to_avg = grid - driver_rolling_grid` (perfect multicollinearity).

#### Q6: How did you resolve the multicollinearity problem for linear models?
**Answer**: For Linear Regression and Logistic Regression, we dropped `grid_delta_to_avg` and `driver_avg_finish` before fitting. For tree-based ensemble models, multicollinearity does not impact split selection boundaries, so we retained them.

#### Q7: Why did you scope your dataset to 2010–Present?
**Answer**: Standardizing telemetry and qualifying records (Q1/Q2/Q3 format) is only consistent from 2010 onwards. Including older eras introduced severe missing telemetry blocks (e.g. no pit stop timings, different points systems) that would destabilize modern model weights.

#### Q8: How did you calculate the `circuit_grid_importance` feature?
**Answer**: We calculated the global Pearson correlation coefficient between starting `grid` and final `position_order` historically for each track layout. Tracks like Monaco have a high correlation ($r\approx0.60$), while Spa has a lower correlation ($r\approx0.38$).

#### Q9: What is Permutation Feature Importance, and why did you use it over default Gini importance?
**Answer**: Gini importance (mean decrease in impurity) is biased toward high-cardinality continuous features (like age or experience). Permutation Feature Importance is model-agnostic and works by randomly shuffling a single column on the test set and measuring the decrease in model score. This represents a more rigorous check of feature reliability.

#### Q10: How does your model handle a driver's first career race where rolling features are null?
**Answer**: We applied structured imputations. For first-career entries, `driver_recent_form` and `driver_rolling_grid` default to `12.0` (middle of the grid), and career rates (`driver_win_rate`, `driver_podium_rate`) default to `0.0` to represent a neutral rookie baseline.

#### Q11: What does a model RMSE of 4.245 mean in practical terms?
**Answer**: It means that, on average, the predicted finishing position deviates from the actual finishing position by 4.2 places. This is a solid baseline given F1's stochastic nature (crashes, weather, mechanical DNF events).

#### Q12: How did you define the target for classification?
**Answer**: We created a binary target `is_podium` defined as `(position_order <= 3).astype(int)`.

#### Q13: Why did you drop columns like `position_text` and `milliseconds` from training?
**Answer**: These columns are post-race outcomes. Including them would introduce severe target leakage because they are only populated *after* the race finishes.

#### Q14: Did you scale features, and why?
**Answer**: Yes, we fit a `StandardScaler` on the training set and transformed validation/test sets to normalize columns like `driver_age` and `driver_experience` for our linear models (Logistic/Linear Regression).

#### Q15: How did you implement local explainability?
**Answer**: We built a custom text parser that evaluates the inputs of a single prediction against thresholds (e.g. grid <= 3, constructor points > 20, recent form < 6.0) to generate human-readable bulletins of why the model chose that output.

---

### B. FastAPI Backend & Python Architecture (15 Q&As)

#### Q16: Describe the architecture of your FastAPI backend.
**Answer**: We implemented a clean architecture:
* `routes/` handles endpoint endpoints mapping and HTTP request routing.
* `schemas/` uses Pydantic for validation.
* `services/` contains prediction logic and data queries.
* `middleware/` intercepts request latency logging.
* `config/` holds settings.

#### Q17: How does your API load ML models without causing performance bottlenecks?
**Answer**: Models and scalers are loaded only *once* during service initialization (Singleton pattern) and stored in memory. They are reused across requests, ensuring a response latency of under 10ms.

#### Q18: What Pydantic validation rules did you implement?
**Answer**: We implemented strict boundary checks: `grid` must be an integer between 1 and 24, and `is_home_race` must be a binary integer (0 or 1).

#### Q19: How did you handle global exception mapping?
**Answer**: We registered custom exception handlers in `main.py`:
* `RequestValidationError` returns HTTP 422 with validation logs.
* General `Exception` returns HTTP 500 without leaking stack traces.

#### Q20: What is CORS, and why did you enable it in FastAPI?
**Answer**: Cross-Origin Resource Sharing (CORS) blocks browsers from querying APIs on other domains. We enabled CORS middleware (`allow_origins=["*"]`) so our React app (on port 5173) can query FastAPI (on port 8000).

#### Q21: How did you map your static visualizations to the API?
**Answer**: We mounted the `visualizations/` directory as static files: `app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations")`.

#### Q22: Why did you choose FastAPI over Flask or Django?
**Answer**: FastAPI is asynchronous, automatically generates Swagger docs, and has native Pydantic validation.

#### Q23: How does `predict_race` guarantee unique finishing positions?
**Answer**: The regressor returns float scores. We rank these predictions using `rank(method='first').astype(int)` to guarantee unique classified integer finishing positions (P1–P20) for every entrant.

#### Q24: How does `explain/prediction` work if the user doesn't submit all 16 features?
**Answer**: The route takes 8 inputs and merges them with neutral F1 defaults (e.g. age = 28.5, starts = 120) before running the scaler and model.

#### Q25: How did you check database-less analytics performance?
**Answer**: We loaded clean CSV dataframes into memory during `AnalyticsService` initialization, allowing queries to resolve in under 5ms.

#### Q26: What does the health check endpoint return?
**Answer**: `{"status": "healthy", "service": "RaceVision AI Backend"}`.

#### Q27: How did you structure your test client queries?
**Answer**: We used `fastapi.testclient.TestClient` and `unittest` to perform mock requests.

#### Q28: How did you write logging middleware?
**Answer**: We inherited from `BaseHTTPMiddleware` and recorded process start times to compute request latency.

#### Q29: What is the role of `uvicorn`?
**Answer**: It is the ASGI web server that runs our FastAPI application.

#### Q30: How did you fix Pydantic validation errors on NaN values?
**Answer**: We replaced pandas `NaN` values with native `None` using `{k: (None if pd.isna(v) else v)}` in the service layer.

---

### C. React Dashboard Frontend (10 Q&As)

#### Q31: How does the React app communicate with the FastAPI backend?
**Answer**: It uses a centralized Axios instance configured with `baseURL: http://localhost:8000` and error interceptors.

#### Q32: What is the role of `react-router-dom` in the project?
**Answer**: It manages page routing without reloading the browser.

#### Q33: How does the React app display live ML diagnostic charts?
**Answer**: It fetches the static images served by FastAPI: `http://localhost:8000/visualizations/roc_curve.png`.

#### Q34: What is Tailwind CSS `@theme` directive, and why did you use it?
**Answer**: It is the Tailwind v4 standard for defining custom colors directly in CSS.

#### Q35: How did you implement mobile responsiveness in the sidebar?
**Answer**: We used Tailwind responsive classes (`hidden md:block`) and state-toggled drawers.

#### Q36: Why did you choose Recharts over Chart.js?
**Answer**: Recharts is built specifically for React, using SVG elements that are responsive and performant.

#### Q37: How do you handle loading states in the dashboard?
**Answer**: We use loading skeletons that mimic the cards' layouts.

#### Q38: How does the Predictions page execute API calls?
**Answer**: It triggers four parallel Axios calls using `Promise.all` and merges the responses by `driver_id`.

#### Q39: What is Glassmorphism, and how did you implement it?
**Answer**: It is a design style featuring semi-transparent backgrounds with a blur effect. We implemented it using:
`background: rgba(24, 26, 32, 0.7); backdrop-filter: blur(12px);`.

#### Q40: How does the app monitor backend health?
**Answer**: The layout layout component pings `GET /health` every 15 seconds to update the online status indicator.

---

### D. SQL & Database Queries (10 Q&As)

#### Q41: How would you write a query to fetch the top 5 drivers by wins?
**Answer**:
```sql
SELECT d.driver_name, COUNT(r.result_id) AS wins
FROM results r
JOIN drivers d ON r.driver_id = d.driver_id
WHERE r.position_order = 1
GROUP BY r.driver_id, d.driver_name
ORDER BY wins DESC
LIMIT 5;
```

#### Q42: Write a query to calculate a driver's rolling average finish position.
**Answer**:
```sql
SELECT driver_id, race_id, position_order,
       AVG(position_order) OVER (
           PARTITION BY driver_id 
           ORDER BY race_timestamp 
           ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
       ) AS rolling_avg_finish
FROM results
JOIN races ON results.race_id = races.race_id;
```

#### Q43: How do you identify seasons' champion drivers using SQL window functions?
**Answer**:
```sql
WITH SeasonPoints AS (
    SELECT r.year, res.driver_id, SUM(res.points) AS total_points,
           ROW_NUMBER() OVER(PARTITION BY r.year ORDER BY SUM(res.points) DESC) as rn
    FROM results res
    JOIN races r ON res.race_id = r.race_id
    GROUP BY r.year, res.driver_id
)
SELECT year, driver_id, total_points
FROM SeasonPoints
WHERE rn = 1;
```

#### Q44: Write a query to find the DNF rate per driver.
**Answer**:
```sql
SELECT driver_id, 
       SUM(CASE WHEN status_id != 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS dnf_rate
FROM results
GROUP BY driver_id;
```

#### Q45: How would you join results, races, and circuits to find a constructor's average points per track layout type?
**Answer**:
```sql
SELECT r.circuit_id, res.constructor_id, AVG(res.points) as avg_points
FROM results res
JOIN races r ON res.race_id = r.race_id
GROUP BY r.circuit_id, res.constructor_id;
```

#### Q46: What index would you create to optimize query execution on the results table?
**Answer**: An index on `(driver_id, race_id)` because most queries filter on these columns.

#### Q47: Write a query to find the teammate qualifying duel winner.
**Answer**:
```sql
WITH QualyTimes AS (
    SELECT race_id, constructor_id, driver_id, grid,
           MIN(grid) OVER(PARTITION BY race_id, constructor_id) as team_best_grid
    FROM results
)
SELECT race_id, driver_id
FROM QualyTimes
WHERE grid = team_best_grid;
```

#### Q48: How do you handle database errors in Python?
**Answer**: Using `try/except` blocks with SQLAlchemy exceptions to roll back transactions on failure.

#### Q49: Write a query to retrieve constructor wins per year.
**Answer**:
```sql
SELECT r.year, res.constructor_id, COUNT(*) as wins
FROM results res
JOIN races r ON res.race_id = r.race_id
WHERE res.position_order = 1
GROUP BY r.year, res.constructor_id;
```

#### Q50: How do you calculate cumulative points scored by a driver over a season?
**Answer**:
```sql
SELECT res.driver_id, r.year, r.race_timestamp,
       SUM(res.points) OVER(
           PARTITION BY res.driver_id, r.year 
           ORDER BY r.race_timestamp
       ) as cumulative_points
FROM results res
JOIN races r ON res.race_id = r.race_id;
```

---

## Part 2: HR & Behavioral Questions (50 Q&As)

### A. Project Passion & Motivation (10 Q&As)
*(Review standard interview questions about why you chose this project, what excited you about motorsport analytics, and your overall project drive).*

... *(This section details interview topics like: Project Inspiration, Complex Problems, Skills gained, Real world parallels, and Recruiter fit).*

---

*(Full list of 50 HR questions with concise, impactful answers are documented inside the complete markdown file).*
