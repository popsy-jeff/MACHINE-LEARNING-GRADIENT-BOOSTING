# Rossmann Sales & Financing — React + FastAPI

A full rewrite of the Streamlit app as a custom React frontend talking to a
FastAPI backend — built this way specifically so the interface is easy to
restyle by hand (plain CSS files, no framework-controlled components).

## Structure

```
backend/     FastAPI app — model, feature pipeline, business logic, API
frontend/    React (Vite) app — pages, sidebar, charts
```

## 1. Run the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Runs at `http://localhost:8000`. It starts on a small **demo model** trained
on synthetic data until you drop in your real one (see below), so the app is
fully click-through-able immediately.

### Connect your real trained model

From your notebook, right after training:

```python
import joblib, json, os
os.makedirs("models", exist_ok=True)  # or point this at backend/models directly

joblib.dump(final_model, "models/rossmann_sales_model.pkl")
joblib.dump(feature_cols, "models/feature_cols.pkl")
json.dump({
    "rmspe": search.best_value,
    "n_trials": len(search.trials),
    "best_params": search.best_params,
}, open("models/validation_metrics.json", "w"), indent=2)
```

Copy those three files into `backend/models/`, restart the backend — the
Home page will show "Loaded trained model" instead of the demo-model warning.

## 2. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173` by default and expects the backend at
`http://localhost:8000`. To point it elsewhere, create `frontend/.env`:

```
VITE_API_URL=http://your-backend-host:8000
```

## Where to edit the visuals

- `frontend/src/index.css` — global design tokens (colors, fonts, 3D button/card styles)
- `frontend/src/components/Sidebar.jsx` + `Sidebar.css` — sidebar layout and nav items
- `frontend/src/components/Viz.jsx` — chart/KPI/pill components used across every page
- `frontend/src/pages/*.jsx` — one file per page, plain JSX/HTML structure

Everything is plain React + CSS — no Streamlit constraints, so any of this
can be restyled directly.

## Pages / API endpoints

| Page | Endpoint |
|---|---|
| Single Prediction | `POST /api/predict` |
| Batch Prediction | `POST /api/predict/batch` (CSV upload) |
| Model Performance | `GET /api/model/metrics` |
| Advance Calculator | `POST /api/advance/offer` |
| Risk Dashboard | `GET /api/audit/log`, `GET /api/audit/log/csv` |

## Known limitations / next steps

- CORS is currently wide open (`allow_origins=["*"]`) — fine for local dev,
  tighten this before deploying anywhere public.
- The decision log is a flat CSV file (`backend/logs/decision_log.csv`) —
  fine for a demo, but swap for a real database before this handles live
  lending decisions.
- Business constants (advance factor, risk-tier thresholds) live in
  `backend/business_logic.py` and are placeholders — not calibrated numbers.
