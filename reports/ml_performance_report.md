# Machine Learning Performance Report – RaceVision AI

This document compiles the model performance metrics, algorithms comparison tables, hyperparameter tuning outputs, and verification predictions for the **RaceVision AI** platform.

---

## 1. Regression Model Comparison (Classified Finishing Position)

The target variable is the integer rank `position_order` representing the driver's final position. The models are evaluated on the Test Set (2021 Season).

### Regression Comparison Table
| Algorithm | MAE (Lower is Better) | MSE (Lower is Better) | RMSE (Lower is Better) | R² Score (Higher is Better) |
| :--- | :---: | :---: | :---: | :---: |
| Extra Trees | 3.311 | 18.022 | 4.245 | 0.458 |
| Random Forest | 3.312 | 18.053 | 4.249 | 0.457 |
| Gradient Boosting | 3.434 | 18.643 | 4.318 | 0.439 |
| Linear Regression (OLS) | 3.362 | 19.445 | 4.410 | 0.415 |
| Decision Tree | 3.389 | 19.614 | 4.429 | 0.410 |

### Selected Best Regressor: `Extra Trees`
* **Test RMSE**: `4.245` positions.
* **Why it won**: Tree-based ensembles (Random Forest, Gradient Boosting) naturally handle non-linear grids and high-cardinality interaction terms (like track grid importance), outperforming basic OLS Linear Regression.

---

## 2. Classification Model Comparison (Podium Finish Probability)

The target variable is the binary indicator `is_podium` (1 if position <= 3, else 0). Models are evaluated on F1 Score on the Test Set (2021 Season).

### Classification Comparison Table
| Algorithm | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Random Forest Classifier | 0.909 | 0.760 | 0.576 | 0.655 | 0.926 |
| Logistic Regression | 0.905 | 0.750 | 0.545 | 0.632 | 0.912 |
| Gradient Boosting Classifier | 0.898 | 0.733 | 0.500 | 0.595 | 0.922 |

### Selected Best Classifier: `Random Forest Classifier`
* **Test F1 Score**: `0.655`
* **Why it won**: Ensemble classifiers are highly robust against class imbalances (podiums represent only ~15% of entrants) and prevent overfitting by averages bagging or gradient boosting steps.

---

## 3. Visual Performance Analyses

### A. Prediction vs. Actual Positions
![Prediction vs Actual](file:///C:/Users/ayaan/.gemini/antigravity-ide/brain/b3bd0ca0-fa31-4d3d-9a70-720d20a23965/images/prediction_vs_actual.png)
* **Insight**: Shows the model's accuracy mapping across positions. A tighter grouping around the red dotted diagonal indicates better position tracking.

### B. Residual Analysis (Prediction Errors)
![Residuals](file:///C:/Users/ayaan/.gemini/antigravity-ide/brain/b3bd0ca0-fa31-4d3d-9a70-720d20a23965/images/residual_analysis.png)
* **Insight**: Focuses on heteroscedasticity. Points are uniformly distributed around the zero line, indicating no systematic over/underforecasting biases.

### C. Feature Importance Profiling
![Feature Importance](file:///C:/Users/ayaan/.gemini/antigravity-ide/brain/b3bd0ca0-fa31-4d3d-9a70-720d20a23965/images/feature_importance_ml.png)
* **Insight**: Highlights that starting `grid` is the most powerful baseline predictor, followed by rolling driver form and constructor strength metrics.

### D. Prediction Error Distribution
![Error Distribution](file:///C:/Users/ayaan/.gemini/antigravity-ide/brain/b3bd0ca0-fa31-4d3d-9a70-720d20a23965/images/error_distribution_ml.png)
* **Insight**: Displays a symmetric, zero-centered distribution of error terms, confirming that the residuals behave normally.

---

## 4. Reusable Inference Pipeline (`RacePredictor`)

We have created a modular, production-ready inference pipeline `RacePredictor` inside `src/pipelines/train_models.py` which:
1. Loads preprocessing scalers and best models.
2. Accepts raw data for a new weekend's race grid.
3. Automatically standardizes columns.
4. Predicts raw positions and converts them to **dense integer ranks** (P1-P20) to ensure no duplicate positions exist.
5. Predicts podium probabilities, **Driver Performance Scores (0-100)**, and **Team Performance Scores (0-100)**.
6. Does NOT require retraining to run.

---

## 5. Machine Learning Readiness Summary
* **Model Serialization**: Models saved to [`models/best_regressor.joblib`](file:///C:/Project/RaceVision AI/models/best_regressor.joblib) and [`models/best_classifier.joblib`](file:///C:/Project/RaceVision AI/models/best_classifier.joblib).
* **Scalers Serialization**: Preprocessing scaling object saved to [`models/scaler.joblib`](file:///C:/Project/RaceVision AI/models/scaler.joblib).
* **ML Readiness Checklist**:
  * [x] Proper split: 2010-2018 train, 2019-2020 validation, 2021 test (chronological split).
  * [x] Multicollinearity drop rules executed for linear classifiers.
  * [x] Hyperparameters tuned using GridSearchCV.
  * [x] Saved models and scaler cleanly to `models/` directory.
