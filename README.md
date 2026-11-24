# 🏋️ Fitness Intelligence Studio

An end-to-end, cloud-ready fitness intelligence suite that combines unsupervised machine learning, sports-science physiology, and personalized program generation. 

The studio consists of two powerful applications integrated into a single Streamlit website:
1. **Member Intelligence (Segmentation & Clustering):** Discovers actionable fitness personas from gym data using a CRISP-DM pipeline.
2. **Personal Training (Workout & Nutrition Recommender):** Turns a 3-step assessment into a downloadable training and nutrition plan.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-app-red)
![Plotly](https://img.shields.io/badge/Plotly-visualisation-purple)
![fpdf2](https://img.shields.io/badge/PDF-fpdf2-purple)

---

## 🚀 Live Deployment (Cloud Edition)

This repository is optimized for **Streamlit Community Cloud**, allowing visitors to access the full suite via a single public URL with zero setup.

### How to Deploy
1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using your GitHub account.
2. Click **Create app** and select this repository.
3. Set the **Main file path** to `streamlit_app.py`.
4. (Optional) Under Advanced Settings, choose Python 3.12 or 3.13.
5. Deploy. No API keys or secrets are required.

*Note: The Cloud Edition uses Streamlit's `session_state` for cross-app data handoff, ensuring privacy and eliminating the need for local file sharing.*

---

## 💻 Local Development (Optional)

To run the unified app locally:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

*(Legacy Note: Older versions of this repository relied on running three separate apps on ports 8500, 8501, and 8502. The current `streamlit_app.py` entrypoint replaces this multi-port architecture with a unified single-server experience.)*

---

## 🧠 Application Overview

### 1. Member Intelligence (Segmentation & Clustering)
A CRISP-DM-structured pipeline that proves clustering is meaningful, not just a pretty scatter plot.

* **Datasets:** Switch between **Real Kaggle Data** (973 rows of honest, continuous gym sessions) and **Synthetic Data** (973 rows generated with 10 known personas for ground-truth validation).
* **Physiological Feature Engineering:** Raw BPM is age-confounded, so the app engineers `HRR_pct` (% heart-rate reserve), `Kcal_per_min` (calorie burn rate), and `Weekly_Volume_hrs` (training load).
* **Modeling Bake-off:** Compares 9 algorithms (K-Means, Agglomerative, GMM, DBSCAN, HDBSCAN, etc.) using Silhouette, Davies-Bouldin, Calinski-Harabasz, and Adjusted Rand Index (ARI).
* **Key Finding:** Multicollinearity is the silent killer of clustering. De-duplicating features (e.g., dropping `Weight` for `BMI`) and using `HRR_pct` lifted persona recovery from ARI 0.59 to 0.74 on synthetic data.
* **Auto-Named Personas:** Discovers and names 14 archetypes (e.g., *HIIT Warrior, Weekend Warrior, Plateau Veteran*) with recommended business actions.

### 2. Personal Training (Workout & Nutrition Recommender)
A 3-step wizard that outputs a complete, downloadable program.

* **Persona Assignment:** Uses a K-Means model (`k=4`) trained on six user-provided features (age, BMI, body fat, frequency, experience, session length).
* **Calorie Prediction:** Blends a Gradient-Boosted Regressor (R² = 0.997, MAE = 12.4 kcal) with the MET equation for robust per-session calorie estimates.
* **Physiology Engine:** Calculates Mifflin-St Jeor BMR, activity-adjusted TDEE, Tanaka HRmax (208 - 0.7×age), Karvonen HR zones, and WHO waist-to-hip risk categories.
* **Actionable Output:** Generates a weekly workout split (Full Body → PPL / Upper-Lower), nutrition macros, hydration targets, and a downloadable PDF report.

---

## 🔗 Cross-App Member Handoff

You can seamlessly transfer a dataset member from **Member Intelligence** to **Personal Training**:
1. Go to **Member Intelligence → Deployment**.
2. Select a real dataset member and click **Connect to Personal Training**.
3. Review and approve the measurements.
4. Click **Prepare profile transfer → Continue**.
5. The training app will automatically open with the member's valid, in-range metrics prefilled.

**Rules & Privacy:**
* Only supported, in-range measurements are prefilled. Out-of-range/missing values remain editable defaults.
* Goals, body-focus, and availability are **never inferred**.
* Personas are recalculated in the training app; cluster IDs are model-specific.
* Transfers are handled via session state (no personal data is saved in URLs).

---

## 🗂️ Project Structure

```text
fitness-studio/
├── streamlit_app.py        # Unified entrypoint and navigation
├── bridge.py               # Cross-page profile handoff (session state)
├── theme.py                # Evergreen/Slate design system
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Native widget styling
├── pages/                  # Streamlit multipage routing
└── projects/
    ├── segmentation/       # CRISP-DM ML Pipeline
    │   ├── app.py
    │   └── data/           # Real & Synthetic CSVs
    └── training/           # Recommender Engine
        ├── workout_recommender_app.py
        ├── recommendation_engine.py
        ├── exercise_library.py
        ├── pdf_report.py
        └── data/           # Kaggle CSVs
```

---

## 🎨 Design System (Evergreen/Slate)

The app uses a unified, custom theme across all pages and PDF reports:
* **Background:** `#0B1220`
* **Surface:** `#141F30`
* **Mint (Accent):** `#5EE0B5`
* **Soft Blue:** `#8AB4F8`
* **Primary Text:** `#F1F5F9`
* **Muted Text:** `#ACBBD0`

---

## ⚖️ Honesty & Safety Disclaimer

* **Not Medical Advice:** All training and nutrition estimates are population-level approximations and educational portfolio demonstrations. They are not clinical advice.
* **Model Transparency:** The calorie regressor's near-perfect R² (~0.99) reflects the Kaggle dataset being near-deterministic (calories are essentially a closed-form function of HR × duration). The app discloses this and treats numbers as *relative intensity guidance*, not lab values.
* **Cloud Limitations:** Free Streamlit hosting can sleep or have resource limits. No uptime guarantee is implied.

---

## 📊 Data Source
* **Real Data:** [Kaggle Gym Members Exercise Dataset](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)
* **Synthetic Data:** Generated via `generate_data.py` with modelled heart-rate physiology.

---

*Created by [Fotros](https://github.com/fotroslab) · Fitness Intelligence Studio
