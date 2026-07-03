# Contributing to RaceVision AI

Thank you for showing interest in contributing to **RaceVision AI**! We welcome bug fixes, documentation updates, features requests, and optimization proposals.

---

## 1. Code of Conduct
By contributing to this repository, you agree to maintain a professional, clean, and collaborative environment.

---

## 2. Setting Up Your Development Environment

### A. Backend Setup
1. Fork and clone the repository.
2. Create a python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   python -m uvicorn src.main:app --reload
   ```

### B. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run Vite development server:
   ```bash
   npm run dev
   ```

---

## 3. Running Test Suites
Before submitting any pull requests, confirm that all API and schema validation test suites pass:
```bash
python tests/test_api.py
```

---

## 4. Coding Standards
* Keep python files PEP 8 compliant, using clean naming conventions and explicit type hints.
* Ensure all endpoints schema validation models are declared using Pydantic.
* Never push raw model binaries (`.joblib`) or secrets to Git; configure them inside local `.env` setups.
