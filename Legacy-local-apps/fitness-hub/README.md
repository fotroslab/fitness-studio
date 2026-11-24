# Fitness Intelligence Studio

Unified landing + Evergreen/Slate theme + explicit cross-app member handoff.
Keep the three project folders as siblings. Each app remains independently runnable.

Run each command in a separate terminal, from its own project directory:

```
# fitness-hub
python -m streamlit run app.py --server.port 8500 --server.address 0.0.0.0
# gym-member-segmentation
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# workout-recommender
python -m streamlit run workout_recommender_app.py --server.port 8502 --server.address 0.0.0.0
```

Open http://localhost:8500. Install dependencies from both apps' requirements.txt first.
Project 1 → Deployment → Connect to Personal Training → select a dataset row,
review measurements and approve → Prepare profile transfer → Continue.
Only supported, in-range measurements are prefilled. Out-of-range/missing values
remain editable defaults. Goals, body-focus and availability are never inferred.
Persona is recomputed by Project 2; cluster labels are model-specific.

Transfers are private random-token links, valid for 30 minutes. JSON records live
in sibling `.fitness-transfers`; expired records are purged on the next export.
This is a same-machine development handoff, not a production authenticated service.
Do not expose publicly without authentication, TLS and scheduled cleanup.
Set FITNESS_TRANSFER_DIR identically on all apps for a custom shared store.
Set FITNESS_URL_8500 / FITNESS_URL_8501 / FITNESS_URL_8502 to override navigation
(e.g. if using different Windows ports or separate deployment hosts).
Default local links use 8500/8501/8502; Arena preview hosts are detected automatically.

Palette: background #0B1220, surface #141F30, mint #5EE0B5,
soft blue #8AB4F8, primary text #F1F5F9, muted text #ACBBD0.
Native Streamlit widgets use .streamlit/config.toml. Charts and PDF accents match.
