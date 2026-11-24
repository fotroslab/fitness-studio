# Fitness Intelligence Studio

A unified, multi-app fitness intelligence suite made of three independently runnable Streamlit projects:

1. **Fitness Hub** — landing page and cross-app member handoff
2. **Gym Member Segmentation & Clustering** — unsupervised persona discovery
3. **Personalized Workout & Nutrition Recommender** — assessment-to-program generator

The three project folders must remain **siblings**. Each app can still be run on its own.

---

## Repository layout

```text
fitness-studio/
├── fitness-hub/
│   ├── app.py
│   ├── bridge.py
│   ├── theme.py
│   ├── README.md
│   └── .streamlit/
├── gym-member-segmentation/
│   ├── app.py
│   ├── bridge.py
│   ├── generate_data.py
│   ├── theme.py
│   ├── requirements.txt
│   ├── README.md
│   ├── data/
│   └── .streamlit/
└── workout-recommender/
    ├── workout_recommender_app.py
    ├── recommendation_engine.py
    ├── exercise_library.py
    ├── pdf_report.py
    ├── bridge.py
    ├── theme.py
    ├── requirements.txt
    ├── README.md
    ├── data/
    └── .streamlit/
```

---

## Quick start

### Prerequisites

- Python 3.10+
- Install dependencies from each app’s `requirements.txt` where present:

```bash
cd gym-member-segmentation
python -m pip install -r requirements.txt

cd ../workout-recommender
python -m pip install -r requirements.txt
```

### Run the three apps

Run each command **from its own project directory**, in a separate terminal. Do not run them from the repository root.

| App | Directory | Command | Port |
|---|---|---|---|
| Fitness Hub | `fitness-hub` | `python -m streamlit run app.py --server.port 8500 --server.address 0.0.0.0` | `8500` |
| Gym Member Segmentation | `gym-member-segmentation` | `python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0` | `8501` |
| Workout Recommender | `workout-recommender` | `python -m streamlit run workout_recommender_app.py --server.port 8502 --server.address 0.0.0.0` | `8502` |

Then open:

```text
http://localhost:8500
```

The landing app links to the other two services. Keep all three terminals running.

### Windows PowerShell example

```powershell
cd "E:\data science lab\fitness studio\fitness-hub"
python -m streamlit run app.py --server.port 8500 --server.address 0.0.0.0
```

```powershell
cd "E:\data science lab\fitness studio\gym-member-segmentation"
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

```powershell
cd "E:\data science lab\fitness studio\workout-recommender"
python -m streamlit run workout_recommender_app.py --server.port 8502 --server.address 0.0.0.0
```

---

## What each app does

### 1. Fitness Hub

- Unified landing page for the suite.
- Evergreen/Slate visual theme.
- Entry point for the cross-app member handoff.
- Explicit flow:
  **Project 1 → Deployment → Connect to Personal Training → select a dataset row → review measurements and approve → Prepare profile transfer → Continue**
- Only supported, in-range measurements are prefilled.
- Out-of-range or missing values remain editable defaults.
- Goals, body-focus, and availability are **never inferred**.
- Persona is recomputed by Project 2; cluster labels are model-specific.

### 2. Gym Member Segmentation & Clustering

A CRISP-DM-structured unsupervised-learning project that turns gym-session data into actionable fitness personas.

Highlights:

- Switchable datasets:
  - **Real Kaggle data** — 973 gym members, continuous behavioural data.
  - **Synthetic 10-persona data** — 973 rows with known ground truth for validation.
- Physiological feature engineering:
  - `HRR_pct` — percentage of heart-rate reserve
  - `Kcal_per_min` — calorie burn rate
  - `Weekly_Volume_hrs` — weekly training load
- Multicollinearity-aware feature selection, log transforms, optional IQR clipping, and multiple scalers.
- Nine clustering algorithms compared head-to-head:
  K-Means, MiniBatch K-Means, Agglomerative Ward, Agglomerative complete, Gaussian Mixture, Spectral, BIRCH, DBSCAN, HDBSCAN.
- Metrics: Silhouette, Davies–Bouldin, Calinski–Harabasz, ARI when ground truth exists, bootstrap stability.
- Auto-named personas with recommended business actions.
- Live scoring for new members and downloadable segmented CSV.
- Synthetic data defaults to `k = 10`; real data defaults to `k = 5` with an explicit trade-off discussion.

### 3. Personalized Workout & Nutrition Recommender

A 3-step assessment that produces a complete, downloadable training and nutrition program.

Pipeline:

```text
Assessment (3 steps)
→ K-Means persona (k=4, trained on real data)
→ Weekly split + exercises (rule engine × experience level)
→ Per-session calorie estimate (GBR ⊕ MET blend)
→ BMR/TDEE + macros + hydration + recovery
→ PDF download
```

Includes:

- Persona card and percentile radar chart.
- Weekly workout plan with exercises, sets, reps, rest, equipment, coaching cues, warm-up, cool-down, finishers, calorie estimates, and target HR zones.
- Nutrition and recovery plan with BMR, TDEE, goal-adjusted calories, macro splits, hydration, meal ideas, sleep guidance, and deload advice.
- Progress projections with honest caveats.
- “Show the math” transparency panel and medical disclaimer.
- Downloadable PDF report.

---

## Cross-app member handoff

The handoff is designed for a same-machine development workflow.

- Transfers are private random-token links.
- Links are valid for **30 minutes**.
- JSON records are stored in a sibling `.fitness-transfers` directory.
- Expired records are purged on the next export.
- Persona is recomputed by the segmentation app; labels are model-specific.
- Goals, body-focus, and availability are not inferred during transfer.

### Important security note

This is a **development handoff**, not a production authenticated service.

Do **not** expose it publicly without:

- authentication,
- TLS,
- scheduled cleanup,
- and a proper shared storage design.

---

## Configuration

| Environment variable | Purpose |
|---|---|
| `FITNESS_TRANSFER_DIR` | Custom shared transfer store. Set identically on all apps. |
| `FITNESS_URL_8500` | Override navigation URL for Fitness Hub. |
| `FITNESS_URL_8501` | Override navigation URL for Gym Member Segmentation. |
| `FITNESS_URL_8502` | Override navigation URL for Workout Recommender. |

Default local links use ports `8500`, `8501`, and `8502`. Arena preview hosts are detected automatically.

Use URL overrides if you run the apps on different Windows ports or separate deployment hosts.

---

## Data

| Dataset | Rows | Description |
|---|---:|---|
| Real — Kaggle Gym Members Exercise Dataset | 973 | Demographics, heart-rate metrics, session behaviour, and body composition. Continuous data with weak natural clusters. |
| Synthetic — 10 known personas | 973 | Generated by `generate_data.py`. Ground truth is retained for ARI validation. |

Generate the synthetic dataset:

```bash
cd gym-member-segmentation
python generate_data.py
```

---

## Theme and design system

The landing app uses the Evergreen/Slate palette:

- Background: `#0B1220`
- Surface: `#141F30`
- Mint: `#5EE0B5`
- Soft blue: `#8AB4F8`
- Primary text: `#F1F5F9`
- Muted text: `#ACBBD0`

Native Streamlit widgets are styled through `.streamlit/config.toml`. Charts and PDF accents match the palette.

---

## Tech stack

- Python
- pandas
- NumPy
- scikit-learn
- Plotly
- Streamlit
- fpdf2
- PDF report generation

---

## Troubleshooting

### `Error: Invalid value: File does not exist: app.py`

This happens when you run Streamlit from the repository root instead of the app directory.

Incorrect:

```bash
cd "E:\data science lab\fitness studio"
streamlit run app.py
```

Correct:

```bash
cd "E:\data science lab\fitness studio\gym-member-segmentation"
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Port already in use

Use the URL override variables or change the port flags consistently.

### Handoff link does not work

Make sure:

- all three apps are running,
- ports match the configured URLs,
- and `FITNESS_TRANSFER_DIR` is identical on all apps if you use a custom store.

### Dependencies missing

Install from the relevant app directory:

```bash
python -m pip install -r requirements.txt
```

---

## Status

This repository is a portfolio-grade, local development suite. It is suitable for demos, experimentation, and same-machine workflows. For production use, add authentication, TLS, persistent storage, scheduled cleanup, and proper deployment isolation.
