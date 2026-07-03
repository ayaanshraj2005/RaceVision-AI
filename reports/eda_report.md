# Unified Exploratory Data Analysis (EDA) Report – RaceVision AI

This document contains the merged and unified Exploratory Data Analysis for the **RaceVision AI** platform. It combines all visual charts and statistical investigations into a single, cohesive research artifact.

---

## 1. Visualizations and Core Data Insights

### A. Driver Wins & Dominance (2000 - Present)
![Driver Wins](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\driver_wins.png)

* **What it shows**: Horizontal bar chart of the top 10 F1 drivers by GP wins since 2000, highlighting Lewis Hamilton and Max Verstappen.
* **Why it is important**: Shows extreme driver dominance (skewed success distribution) indicating driver experience is heavily correlated with winning probability.
* **ML Application**: Raw `driverId` values have high cardinality and can overfit. We will transform this into a dynamic numerical feature: **`driver_rolling_win_rate`** or **`driver_career_wins`**.

---

### B. Team Performance & Constructor Podiums (2010 - Present)
![Constructor Podiums](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\constructor_podiums.png)

* **What it shows**: Podium finishes by constructors in the Hybrid/Modern era.
* **Why it is important**: Proves team capability (aerodynamics, engine) is the single most dominant factor in race outcomes, accounting for the vast majority of performance delta.
* **ML Application**: Since teams rebrand, we will use **`constructor_rolling_points`** and **`constructor_championship_rank`** as numerical features so the model trains on car package strength dynamically.

---

### C. Driver Consistency Profiles
![Driver Consistency](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\driver_consistency.png)

* **What it shows**: Boxplot of classified finishing positions for the top 5 F1 drivers in the 2021 season.
* **Why it is important**: Visualizes driver variance. A narrow box (e.g. Verstappen) shows high consistency and predictability, whereas a wide box shows volatile racing outcomes or reliability risks.
* **ML Application**: To represent driver skill profiles, we will engineer **`driver_position_median`** and **`driver_position_std`** over a rolling window.

---

### D. Championship Progression
![Championship Progression](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\championship_progression.png)

* **What it shows**: Cumulative points progression of the top 5 drivers over the 2021 season.
* **Why it is important**: Shows temporal state and development momentum. Flatlines indicate vehicle development plateaus or technical failures.
* **ML Application**: Adds championship pressure. We will engineer **`driver_championship_lead_deficit`** to teach models context about driver pressure.

---

### E. Pole Position Conversion Rates
![Pole Conversion](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\pole_conversion.png)

* **What it shows**: Bar chart mapping the final race classification categories for drivers starting from Pole Position (Grid 1).
* **Why it is important**: Reveals that Pole Position translates to a victory only ~40% of the time, and carries a ~15% retirement (DNF) risk.
* **ML Application**: Teaches classifiers the baseline prior probability of winning when starting first on the grid.

---

### F. Grid Position vs. Finishing Position
![Grid vs Finish](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\grid_vs_finish.png)
![Grid vs Finish Scatter](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\grid_vs_finish_scatter.png)

* **What they show**: 
  1. A line chart showing average finish position by grid start (pole average is ~3.5; bottom grid positions gain positions on average).
  2. A scatter plot of all historical grid starts vs classified positions with a linear trend line (Slope = 0.44).
* **Why it is important**: Confirms that starting grid is the single strongest predictor of race finish, but the relationship has high variance and non-linearity.
* **ML Application**: Slices grid starts. Regression models will need non-linear kernels or tree-based partitions (Random Forest/XGBoost) to accommodate the variance.

---

### G. Circuit Profile Overtaking Delta (Monaco vs. Spa)
![Monaco vs Spa](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\monaco_vs_spa_grid_impact.png)

* **What it shows**: Side-by-side scatter plots comparing grid-to-finish correlations for Monaco ($r pprox 0.60$) and Spa-Francorchamps ($r pprox 0.38$).
* **Why it is important**: Overtaking is circuit-dependent. Qualifying dominates at Monaco (narrow street layout), but Spa allows shuffles (long straights).
* **ML Application**: We will create a track-specific feature **`circuit_grid_importance`** (the track's historical grid-finish Pearson correlation) to dynamically weight grid advantage per track.

---

### H. Telemetry & Lap Pace across Eras (Silverstone GP)
![Fastest Lap Violin](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\fastest_lap_violin.png)
![Lap Time Distribution](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\lap_time_dist.png)

* **What they show**:
  1. Violin plot of fastest lap times at Silverstone across F1 Eras (V10, V8, V6 Hybrid).
  2. Density distribution comparison of lap times for top drivers in a sample Grand Prix.
* **Why it is important**: Shows how rules and tire compounds impact pace. Modern V6 hybrid and V10 lap times are significantly lower than V8s.
* **ML Application**: Absolute lap times are biased by era rules. We will normalize lap times: **`relative_lap_pace_pct`** (individual lap / race median lap) to make pacing generalizable.

---

### I. Pit Stop Operations & Outliers
![Pit Stop Trends](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\pit_stop_trends.png)
![Pit Stop Outliers](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\outliers_pit_stops.png)

* **What they show**:
  1. Historical pit stop duration improvements since 2011 (declined from ~24s average lane duration to ~22s).
  2. Boxplot of pit stop durations under 60 seconds (median stop = 22.8s; stops >30s are anomalies).
* **ML Application**: Stops >30s represent nose-cone changes or car repairs (accidents) rather than planned tire strategy. We will filter out durations >30s when modeling tire strategy.

---

### J. Diagnostics & Correlation
![Correlation Heatmap](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\correlation_heatmap.png)
![Missing Values](file:///C:\Users\ayaan\.gemini\antigravity-ide\brain\b3bd0ca0-fa31-4d3d-9a70-720d20a23965\images\missing_values_audit.png)

* **What they show**:
  1. Pearson correlation matrix of core numerical variables.
  2. Missing value audit showing missing telemetry blocks in historical eras.
* **ML Application**: Highlights collinear variables (e.g. fastest lap speed and fastest lap time). We will select only one to avoid model coefficient inflation.

---

## 2. Statistical Diagnosis & Data Quality Gaps

### A. Skewness
* **Grid Skewness**: `0.190` (Symmetrical, as expected for sequential grid positions).
* **Finishing Position Skewness**: `0.390` (Uniform distribution).

### B. Class Imbalance (DNFs)
* **Finished Classifications**: `6,821` (`26.8%`)
* **Retirements / DNFs**: `18,599` (`73.2%`)
* **Model Impact**: DNFs account for `73.2%` of historical data. When predicting finishing ranks, models must incorporate team reliability indices.

### C. Potential Feature Leakage Columns
* **Columns to Drop**: `position, position_text, points, milliseconds, time, fastest_lap_time, fastest_lap_time_seconds, fastest_lap_speed, rank, fastest_lap`
* **ML Rule**: These columns represent post-race information (points scored, milliseconds, actual fast lap timings). **They must be deleted before model training** to prevent leakage.

---

## 3. Recommended ML Feature Roadmap

### Recommended Features to Keep/Engineer
1. **`grid`** (Raw start position - anchor baseline).
2. **`driver_rolling_form_3_races`** (Rolling average finish).
3. **`constructor_rolling_points`** (Team package strength proxy).
4. **`circuit_grid_importance`** (Track grid-advantage Pearson correlation).
5. **`driver_circuit_experience`** (Track experience count).
6. **`driver_age_at_race`** (Driver age at event).

### Features to Remove (To Prevent Leakage)
1. Post-race outcomes: `points`, `position`, `position_text`, `milliseconds`, `time`.
2. Post-race telemetry: `fastest_lap_time`, `fastest_lap_speed`, `rank`, `fastest_lap`.

### Potential Prediction Challenges
* **Stochastic Failures**: Crash damage or sudden engine blowout represent noise that cannot be captured by past pacing, creating a natural accuracy limit.
* **Incomplete Historical telemetry**: Detailed lap times are pre-1996 null and pit stops are pre-2011 null. Training must restrict scope to modern hybrid eras (2011+ or 2014+) for complete telemetry coverage.
