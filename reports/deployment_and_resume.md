# Deployment Guide, CV Bullet Points & Presentation Pitches – RaceVision AI

This unified document outlines deployment workflows, CV descriptors, GitHub repository configurations, and oral presentation scripts for the **RaceVision AI** platform.

---

## 1. Production Deployment Guide

### A. FastAPI Backend Deployment (Production)
We recommend deploying the FastAPI server to a cloud VM instance (e.g. AWS EC2, GCP Compute Engine, DigitalOcean Droplet) using **Gunicorn** wrapping **Uvicorn** workers and proxied behind **Nginx**.

1. **System Packages & VirtualEnv**:
   ```bash
   sudo apt-get update && sudo apt-get install python3-pip python3-venv nginx git -y
   git clone https://github.com/<your-username>/racevision-ai.git /var/www/racevision-ai
   cd /var/www/racevision-ai
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Systemd Service configuration**:
   Create `/etc/systemd/system/racevision.service`:
   ```ini
   [Unit]
   Description=RaceVision AI FastAPI Application
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/racevision-ai
   ExecStart=/var/www/racevision-ai/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app --bind 127.0.0.1:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. **Nginx Reverse Proxy configuration**:
   Configure `/etc/nginx/sites-available/default` to forward static images and API paths:
   ```nginx
   server {
       listen 80;
       server_name racevision.domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### B. React Frontend Deployment
The Vite React app compiles to a static bundle (`dist/` directory) and can be hosted directly on CDNs like Vercel, Netlify, or AWS S3:
1. **Build Commands**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. **Environment Variables**:
   Configure the production domain pointer inside `.env.production`:
   ```env
   VITE_API_URL=https://racevision-api.domain.com
   ```

---

## 2. Resume & Portfolio bullet points

### Job Titles: Data Scientist | Machine Learning Engineer | Full-Stack AI Engineer

#### Project Title: RaceVision AI – Real-Time Motorsport Analytics & Predictive Modeling Platform
* **Project Summary**: Architected and deployed an end-to-end motorsport analytics platform hosting serialized machine learning models (Extra Trees Regressor, Random Forest Classifier) to forecast classified finishing positions and podium likelihoods in Formula 1 racing, serving outputs via a secure FastAPI backend and an interactive glassmorphic React dashboard.
* **Responsibilities & Achievements**:
  * **Eliminated Target Leakage**: Designed a chronological feature engineering pipeline executing custom group-shifting (`shift(1)`) on driver/constructor career standings, ensuring no post-race outcomes or forward-looking targets leaked into predictor arrays.
  * **Temporal Data Splitting**: Avoided random cross-validation leakage by implementing sequential year-based splits (2010-2018 train, 2019-2020 validation, 2021 test), preserving historical time order.
  * **Multicollinearity Diagnosis**: Conducted Variance Inflation Factor (VIF) audits to detect qualifying pace collinearities, enforcing feature drop criteria for linear estimators to prevent coefficient inflation.
  * **Optimized Ensemble Models**: Tuned hyperparameters using GridSearchCV, selecting an Extra Trees Regressor (Test RMSE: 4.245) and a Random Forest Classifier (Test F1 Score: 0.655, ROC-AUC: 0.926) to manage high class imbalances.
  * **Model-Agnostic Explainability**: Configured Permutation Feature Importance showing starting `grid` starts represent the dominant outcome anchor.
  * **High-Performance FastAPI**: Implemented a database-less service layer caching clean CSV datasets in-memory to serve analytics APIs in under 5ms and ML inferences in under 30ms.

---

## 3. GitHub Metadata & Release Notes (v1.0)

* **Suggested Repository Name**: `racevision-ai-analytics`
* **Repository Description**: "End-to-end motorsport machine learning and analytics platform. Built with Python, Extra Trees, FastAPI, React (Vite), Tailwind CSS, and Recharts. Prevents target leakage using chronological shifting and implements Permutation explainability."
* **Topics/Tags**: `machine-learning`, `data-science`, `fastapi`, `react`, `formula1`, `predictive-analytics`, `explainable-ai`, `recharts`, `scikit-learn`
* **Release Notes (v1.0.0)**:
  * Serialized Extra Trees Regressor model (RMSE 4.245) and Random Forest Classifier (ROC-AUC 0.926).
  * Packaged `RacePredictor` inference pipeline.
  * REST API routing with CORS, request validations, and latency logging middleware.
  * Interactive UI dashboard with glassmorphism panels.

---

## 4. Oral Presentation Scripts

### A. The 2-Minute Elevator Pitch (For Recruiters)
> "Hi! I recently built **RaceVision AI**, an advanced analytics and machine learning platform for Formula-style motorsport predictions. 
> F1 races are incredibly noisy, and predicting outcomes is historically difficult due to severe class imbalances and grid starting advantages. 
> To solve this, I designed a pipeline that isolates the modern Hybrid era, engineers features chronologically using shifting methods to prevent target leakage, and trains ensemble tree models to predict finishing order and podium chances. 
> I built the backend in FastAPI, which loads the serialized models to run inference in under 30 milliseconds, and exposes analytics to a premium dark-themed React dashboard. 
> It's a complete production-style showcase demonstrating my ability to build clean, leak-free machine learning systems and package them into production-ready web applications."

### B. The 5-Minute Technical Walkthrough (For Engineers & Hiring Managers)
> "In building **RaceVision AI**, my main objective was to showcase rigorous data science standards rather than just training basic models.
> F1 data is sequential, so standard K-Fold cross-validation introduces target leakage. I resolved this by splitting data chronologically: training on 2010–2018, validating on 2019–2020, and testing on 2021. 
> For feature engineering, I computed rolling driver form, team strength, and track grid correlations. To ensure no forward-looking bias, I sorted entries chronologically and shifted all targets by one race prior to computing rolling stats. This guarantees the model uses only information available *before* the race begins.
> I performed multicollinearity analysis using Variance Inflation Factors. This highlighted perfect collinearity in my qualifying metrics because grid delta is a direct linear combination of current grid and rolling grid. I adjusted my model paths to exclude these columns for linear estimators, while retaining them for tree ensembles.
> I selected an Extra Trees Regressor for finishing order predictions and a Random Forest Classifier for podium probabilities. Using GridSearchCV, I optimized F1 score to account for class imbalance, yielding a 92% ROC-AUC. 
> To make predictions interpretable, I integrated Permutation Feature Importance to identify grid starts as the dominant feature, and wrote local explainability rules to generate human-readable explanations.
> The FastAPI backend serves these models and caches CSV data in-memory for sub-5ms analytics lookups. The frontend React client is styled with a custom dark glassmorphism theme, rendering Recharts visualizations and interactive predictions. It's fully modular and verified via production builds."
