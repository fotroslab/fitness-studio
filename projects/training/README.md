# 💪 Personalized Workout & Nutrition Recommender

A standalone Streamlit application that turns a 3-step assessment into a complete,
downloadable training + nutrition program — powered by **machine learning trained on
973 real gym sessions** (Kaggle Gym Members Exercise Dataset) plus transparent,
auditable sports-science rules.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-app-red)
![fpdf2](https://img.shields.io/badge/PDF-fpdf2-purple)

> Companion project: **Gym Member Segmentation & Clustering** — the persona engine
> this app builds on.

---

## 🧠 How it works

```
Assessment (3 steps)  →  K-Means persona (k=4, trained on real data)
                      →  Weekly split + exercises (rule engine × your level)
                      →  Per-session calorie estimate (GBR ⊕ MET blend)
                      →  BMR/TDEE + macros + hydration + recovery
                      →  PDF download
```

### The three inputs that make it *data-driven*, not a quiz

1. **Persona assignment (unsupervised ML).** A K-Means model (k = 4) is trained on the
   six features a user can actually provide (age, BMI, body fat, training frequency,
   experience, preferred session length). Your nearest centroid determines plan
   intensity and drives the "you vs. persona" radar chart.
2. **Calorie prediction (supervised ML).** A Gradient-Boosted Regressor predicts
   `Calories_Burned` from profile + session features (holdout **R² = 0.997,
   MAE = 12.4 kcal** — the public dataset is near-deterministic, calories are essentially
   a closed-form function of HR × duration; the app says so honestly). The prediction is
   blended 50/50 with the MET equation.
3. **Honest physiology (rules).** Mifflin-St Jeor BMR · activity-adjusted TDEE ·
   goal-based calorie deltas · Tanaka HRmax (208 − 0.7×age) · Karvonen HR zones when
   resting HR is provided · WHO waist-to-hip risk categories · Deurenberg body-fat
   estimate (if unknown).

## 🚀 Run it

```bash
pip install -r requirements.txt
streamlit run workout_recommender_app.py
```

## 🗂️ Project structure

```
├── workout_recommender_app.py  # Streamlit UI — 3-step wizard + 4 result tabs
├── recommendation_engine.py    # Persona model, calorie regressor, physiology, planner
├── exercise_library.py         # 60+ exercises w/ patterns, levels, equipment, cues
├── pdf_report.py               # fpdf2 plan builder (downloadable PDF)
├── theme.py                    # Galaxy / Cosmic Nebula UI theme
└── data/
    └── gym_members_exercise_tracking.csv   # Kaggle dataset (973 rows)
```

## 📋 What the user gets

**Tab 🎭 Your Persona** — K-Means persona card (trained on the dataset, not hard-coded),
alive BMI gauge, percentile radar (you vs. persona centroid), input snapshot.

**Tab 🏋️ Weekly Workout Plan** — split matched to days/goal/experience (Full Body →
PPL / Upper-Lower / 7-day), per-session: exercises with sets×reps, rest, equipment,
coaching cues, focus-match ★, warm-up, cool-down, goal-specific finisher, estimated
calories, target HR zone (Karvonen or %HRmax).

**Tab 🥗 Nutrition & Recovery** — BMR → TDEE → goal-adjusted target, macro split with
keto / high-protein / plant-based overrides, water target gauge, diet-matched meal
ideas, meal timing, sleep & rest-day protocol, deload guidance.

**Tab 📈 Progress & Insights** — 12-week projection with honest caveats, cumulative
weekly burn curve, body-composition dashboard (BMI, body fat, WHR, ideal range), and a
"show the math" transparency panel + medical disclaimer.

## ⚖️ Honesty & safety

- The calorie model's R² ≈ 0.99 reflects the dataset being near-deterministic — the app
  discloses this, and treats numbers as *relative intensity guidance*, not lab values.
- Projections are population estimates; the app tells users so.
- Not medical advice — prominently disclaimed in UI and PDF.

---

*Created by [Fotros](https://github.com/fotroslab) · Gym Member Segmentation & Clustering family ·
[Project 1](https://github.com/fotroslab/Gym-Member-Segmentation)*
