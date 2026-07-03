# Frontend Architecture & Dashboard Documentation – RaceVision AI

This document details the production-ready React (Vite) frontend architecture, page designs, Tailwind CSS configuration, and api integration mappings.

---

## 1. Directory Structure

The React dashboard code is structured cleanly in the `/frontend/src/` folder:

```text
frontend/
 ├── dist/                    # Compiled production build directory
 ├── src/
 │    ├── layouts/
 │    │    └── DashboardLayout.jsx  # Dark theme outline header and side menu
 │    ├── pages/
 │    │    ├── Dashboard.jsx        # KPIs, wins chart, features importance
 │    │    ├── Drivers.jsx          # Selection drop and comparative statistics
 │    │    ├── Teams.jsx            # Constructor podium and win rates charts
 │    │    ├── Circuits.jsx         # Track records table and grid correlation index
 │    │    ├── Predictions.jsx      # Interactive ML predictions interface
 │    │    ├── XAI.jsx              # Local and global explanations consoles
 │    │    ├── Models.jsx           # Model accuracies and diagnostics charts
 │    │    └── Settings.jsx         # Backend status pinging and release profiles
 │    ├── services/
 │    │    └── api.js               # Axios instance query mappings
 │    ├── App.jsx                   # React Router configurations
 │    ├── index.css                 # Base scrollbar, theme colors and glassmorphic styles
 │    └── main.jsx                  # Mount wrapper
 ├── tailwind.config.js             # Tailwind variables configurations
 └── postcss.config.js              # PostCSS v4 configurations
```

---

## 2. API Mappings Configuration
The Axios service in `src/services/api.js` maps each dashboard component directly to its backend API endpoint:

| Page | Frontend Component Action | Backend REST Endpoint |
| :--- | :--- | :--- |
| **Dashboard** | Fetches counters and top standings stats. | `GET /analytics/dashboard` |
| **Drivers** | Populates selector drop and driver details. | `GET /analytics/drivers`, `GET /analytics/drivers/{id}` |
| **Teams** | Populates selector drop and team details. | `GET /analytics/teams`, `GET /analytics/teams/{id}` |
| **Circuits** | Lists F1 track records and grid correlation. | `GET /analytics/circuits` |
| **Predictions** | Dispatches race entries for predictions. | `POST /predict/finish-position`, `POST /predict/podium-probability`, `POST /predict/driver-performance`, `POST /predict/team-performance` |
| **XAI** | Fetches global weights and local explanations. | `GET /explain/feature-importance`, `POST /explain/prediction` |
| **Models** | Loads accuracy scores and displays static charts. | `GET /model/metrics`, `GET /model/information` |
| **Settings** | Pings server health check. | `GET /health`, `GET /version` |

---

## 3. Premium Glassmorphic Design System
The frontend implements CSS variables styling to match our matplotlib dark visualization profile:
* **Background Color**: `#111216` (Carbon dark)
* **Card Backing**: `rgba(24, 26, 32, 0.7)` with `backdrop-filter: blur(12px)`
* **Borders Color**: `rgba(45, 49, 57, 0.6)`
* **Accent Colors**:
  * Green: `#00F29E` (Classification targets)
  * Blue: `#00D4FF` (Stats comparing and indexes)
  * Yellow: `#FFC837` (Wins indicators)
  * Red: `#FF4A6B` (Validation warnings & high correlation tracks)

---

## 4. Frontend Deployment Readiness Checklist
- [x] **Vite Compilation Success**: Verified through `npm run build` with zero errors.
- [x] **FastAPI Backend Integration**: Connected to local development server using Axios.
- [x] **Automatic Health Monitoring**: Sidebar contains a check interval updating server status.
- [x] **No Mock Data**: Reads drivers lists and parameters directly from processed datasets.
- [x] **Charts Integration**: Utilizes responsive Recharts widgets displaying win ratios and ML parameters.
- [x] **Static Image Hosting**: Embeds learning curves and ROC curves served by FastAPI StaticFiles.
