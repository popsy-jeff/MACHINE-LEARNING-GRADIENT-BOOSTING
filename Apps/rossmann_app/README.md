# Rossmann Sales Forecasting & Revenue-Based Financing App

A Streamlit app built around the trained Rossmann XGBoost sales model,
extended into a merchant cash advance product per the workflow doc
(`Sales_Model_Workflow_and_Training_Notes.docx`).

## Structure

```
rossmann_app/
├── Home.py                       # main entry point
├── pages/
│   ├── 1_Single_Prediction.py    # forecast one store/day
│   ├── 2_Batch_Prediction.py     # CSV upload -> forecasts for many rows
│   ├── 3_Model_Performance.py    # validation RMSPE, feature importance
│   ├── 4_Advance_Calculator.py   # Phase 3: 90-day forecast -> advance offer
│   └── 5_Risk_Dashboard.py       # Phase 3/5: flagged applications, audit log
├── utils/
│   ├── feature_pipeline.py       # rebuilds training-time features from raw input
│   ├── model_utils.py            # model loading + prediction (with demo fallback)
│   ├── business_logic.py         # eligibility, advance calc, risk tiering
│   └── audit_log.py              # Phase 5: logs every lending decision
├── models/                       # <- put your real .pkl files here
├── logs/                         # decision_log.csv gets created here automatically
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Plug in your real trained model

The app currently runs on a small **demo model** (synthetic data) so it's
fully click-through-able out of the box. To use your actual trained model:

From your notebook, after your final Optuna-tuned model is trained:

```python
import joblib
joblib.dump(final_model, 'rossmann_sales_model.pkl')
joblib.dump(feature_cols, 'feature_cols.pkl')

import json
metrics = {
    "rmspe": search.best_value,
    "n_trials": len(search.trials),
    "best_params": search.best_params,
}
with open("validation_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
```

Then copy `rossmann_sales_model.pkl`, `feature_cols.pkl`, and
`validation_metrics.json` into this app's `models/` folder. The app
auto-detects them and switches out of demo mode — you'll see a green
"Loaded trained model" message on the Home page instead of the demo
warning.

## Run the app

```bash
streamlit run Home.py
```

## Notes on the feature pipeline

`utils/feature_pipeline.py` reconstructs `CompetitionOpen`, `Promo2Open`,
and `IsPromo2Month` from raw inputs, plus one-hot encodes `StateHoliday`,
`StoreType`, `Assortment`, and `DayOfWeek` — mirroring what was done in
the training notebook. If your real `feature_cols.pkl` has a different
column order or additional engineered columns, the pipeline will still
work (columns are reindexed to match), but double check the demo-mode
warning disappears and a few known Store IDs produce sane predictions
before trusting it for real offers.

## Notes on the business logic (Phase 3)

Tunable parameters (advance factor, haircut %, minimum history, etc.)
live at the top of `utils/business_logic.py` — adjust them there rather
than in the page code, so the numbers stay in one auditable place.
