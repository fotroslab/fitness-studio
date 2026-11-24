"""Recommendation engine — persona assignment + workout & nutrition logic.

Design
------
* **Unsupervised part**: a K-Means persona model trained on the real Kaggle
  gym dataset (973 sessions) using the six features a new user can actually
  provide (age, BMI, body fat %, training frequency, experience, preferred
  session length). The persona is *not* a gimmick — it routes plan intensity
  and supplies the comparison centroid for the radar chart.
* **Supervised part**: a Gradient-Boosted regressor predicts Calories_Burned
  from profile + session features (R² reported in the UI). The prediction is
  blended 50/50 with a MET-based estimate for robustness.
* **Rule-based part**: everything physiological (BMR, TDEE, macros, HR zones,
  weekly split, recovery) is transparent sports-science rules — auditable by
  a human expert, which matters for a portfolio piece.

Everything is framework-free (no streamlit import) so it can be unit-tested
and reused — the Streamlit app (`workout_recommender_app.py`) is a thin shell
over this module.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path(__file__).resolve().parent / "data" / "gym_members_exercise_tracking.csv"

# Features a new user can supply — used to train the persona model.
CLUSTER_FEATURES = [
    "Age",
    "BMI",
    "Fat_Percentage",
    "Workout_Frequency (days/week)",
    "Experience_Level",
    "Session_Duration (hours)",
]

AGE, WEIGHT, HEIGHT = "Age", "Weight (kg)", "Height (m)"
AVG_BPM, SESSION, WORKOUT = "Avg_BPM", "Session_Duration (hours)", "Workout_Type"
FREQ, EXP = "Workout_Frequency (days/week)", "Experience_Level"
CALORIES = "Calories_Burned"


@dataclass
class UserProfile:
    """Everything the assessment form collects, in typed fields."""

    age: int
    gender: str                     # "Male" | "Female"
    height_m: float
    weight_kg: float
    # Body measurements (cm) — context for insights, not clustering inputs.
    arm_cm: float
    waist_cm: float
    thigh_cm: float
    hip_cm: float
    chest_cm: float
    body_fat_pct: float | None      # None → estimated via Deurenberg
    # Fitness profile & goals
    experience: int                 # 1 beginner, 2 intermediate, 3 advanced
    goal: str                       # weight_loss|muscle_gain|endurance|general|flexibility
    body_focus: str                 # full_body|upper_body|lower_body|core_abs|glutes_legs
    days: int                       # training days per week, 1–7
    session_minutes: int            # preferred session length, 30–120
    resting_hr: int | None          # optional — enables Karvonen HR zones
    # Lifestyle & nutrition
    diet: str                       # Omnivore|Vegetarian|Vegan|Keto|High-Protein
    known_calories: float | None    # optional self-reported intake (kcal/day)
    water_liters: float


# ---------------------------------------------------------------------------
# Persona model (K-Means on collectable features)
# ---------------------------------------------------------------------------

class PersonaModel:
    """K-Means persona assignment trained on the real Kaggle dataset."""

    def __init__(self, k: int = 4, random_state: int = 42):
        self.k = k
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=k, n_init=15, random_state=random_state)
        self.centroids_raw: pd.DataFrame | None = None
        self.persona_names: dict[int, str] = {}
        self.persona_desc: dict[int, str] = {}
        self.cluster_sizes: pd.Series | None = None

    def fit(self, df: pd.DataFrame) -> "PersonaModel":
        X = self.scaler.fit_transform(df[CLUSTER_FEATURES])
        labels = self.model.fit_predict(X)
        tmp = df.copy()
        tmp["cluster"] = labels
        self.centroids_raw = tmp.groupby("cluster")[CLUSTER_FEATURES].mean()
        self.cluster_sizes = tmp["cluster"].value_counts().sort_index()
        self._name_personas()
        return self

    def _name_personas(self) -> None:
        """Deterministic rule naming from centroid z-scores."""
        c = self.centroids_raw
        z = (c - c.mean()) / c.std().replace(0, 1)
        for cid in c.index:
            row = z.loc[cid]
            if row[EXP] > 0.5 and row[FREQ] > 0.5:
                name = "High-Output Athlete"
                desc = ("Experienced, trains 4–5 days a week with long sessions — "
                        "needs advanced programming and recovery management.")
            elif row["BMI"] > 0.5:
                name = "Fat-Loss Focus"
                desc = ("Higher body mass — responds best to strength + metabolic "
                        "conditioning and nutrition-first coaching.")
            elif row[EXP] < -0.3:
                name = "Casual Beginner"
                desc = ("Low frequency / experience — needs habit-building, simple "
                        "full-body plans and wins early and often.")
            else:
                name = "Balanced Regular"
                desc = ("Consistent intermediate member — variety and periodic "
                        "progression keep them engaged and growing.")
            self.persona_names[cid] = name
            self.persona_desc[cid] = desc

    def predict(self, profile: UserProfile) -> int:
        bmi_value = bmi(profile.weight_kg, profile.height_m)
        fat = profile.body_fat_pct
        if fat is None:
            fat = estimate_body_fat(bmi_value, profile.age, profile.gender)
        row = pd.DataFrame([{
            "Age": profile.age,
            "BMI": bmi_value,
            "Fat_Percentage": fat,
            FREQ: min(max(profile.days, 2), 5) if profile.days != 3 else 3,
            EXP: profile.experience,
            SESSION: profile.session_minutes / 60.0,
        }])[CLUSTER_FEATURES]
        return int(self.model.predict(self.scaler.transform(row))[0])

    def centroid(self, persona: int) -> pd.Series:
        return self.centroids_raw.loc[persona]

    def size(self, persona: int) -> int:
        return int(self.cluster_sizes.loc[persona])


@lru_cache(maxsize=1)
def get_persona_model() -> PersonaModel:
    df = pd.read_csv(DATA_PATH)
    return PersonaModel(k=4).fit(df)


# ---------------------------------------------------------------------------
# Supervised calorie model (regression) — used with equal weight to MET math
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def train_calorie_model():
    """GBR predicting Calories_Burned. Returns (pipeline, report dict)."""
    df = pd.read_csv(DATA_PATH)
    num = [AGE, WEIGHT, HEIGHT, AVG_BPM, SESSION, FREQ, EXP]
    cat = [WORKOUT, "Gender"]
    X, y = df[num + cat], df[CALORIES]
    pre = ColumnTransformer([
        ("num", StandardScaler(), num),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
    ])
    model = Pipeline([("pre", pre),
                      ("gbr", GradientBoostingRegressor(
                          n_estimators=250, random_state=42, max_depth=3,
                          learning_rate=0.08))])
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                              random_state=42)
    model.fit(X_tr, y_tr)
    pred = model.predict(X_te)
    r2 = float(model.score(X_te, y_te))
    mae = float(np.mean(np.abs(pred - y_te)))
    model.fit(X, y)  # refit on all data for serving
    return model, {"r2": round(r2, 3), "mae": round(mae, 1)}


def predict_session_calories(profile: UserProfile, workout_type: str,
                             duration_hours: float,
                             avg_bpm: float | None) -> float:
    model, _ = train_calorie_model()
    row = pd.DataFrame([{
        AGE: profile.age, WEIGHT: profile.weight_kg, HEIGHT: profile.height_m,
        AVG_BPM: avg_bpm if avg_bpm else 140,
        SESSION: duration_hours,
        FREQ: profile.days, EXP: profile.experience,
        WORKOUT: workout_type, "Gender": profile.gender,
    }])
    reg = float(model.predict(row)[0])
    met = MET_BY_WORKOUT.get(workout_type, 6.0)
    met_est = met * profile.weight_kg * duration_hours
    return round(0.5 * reg + 0.5 * met_est)


def predict_avg_bpm(profile: UserProfile, intensity_lo: float,
                    intensity_hi: float) -> float:
    """Estimate average working HR for a goal-intensity band (Karvonen-style)."""
    max_ = estimate_hr_max(profile.age)
    rest = profile.resting_hr if profile.resting_hr else 62
    mid = (intensity_lo + intensity_hi) / 2
    return rest + mid * (max_ - rest)


# ---------------------------------------------------------------------------
# Physiology helpers
# ---------------------------------------------------------------------------

def bmi(weight_kg: float, height_m: float) -> float:
    return round(weight_kg / height_m**2, 1)


def bmi_category(value: float) -> tuple[str, str]:
    if value < 18.5:
        return "Underweight", "#F1C777"
    if value < 25:
        return "Normal", "#72D5AD"
    if value < 30:
        return "Overweight", "#F1C777"
    return "Obese", "#F38BA0"


def estimate_body_fat(bmi_value: float, age: int, gender: str) -> float:
    """Deurenberg equation — population estimate when no caliper/scan available."""
    sex = 1 if gender == "Male" else 0
    return round(float(np.clip(1.20 * bmi_value + 0.23 * age - 10.8 * sex - 5.4, 5, 50)), 1)


def estimate_hr_max(age: int) -> int:
    """Tanaka formula: 208 − 0.7 × age (more accurate than 220 − age)."""
    return int(round(208 - 0.7 * age))


def hr_zones(hr_max: int, resting: int | None = None) -> list[dict]:
    """Five-zone table. Karvonen (HRR) when resting HR is known, else %HRmax."""
    spans = [("Z1 Recovery", 0.50, 0.60), ("Z2 Endurance", 0.60, 0.70),
             ("Z3 Tempo", 0.70, 0.80), ("Z4 Threshold", 0.80, 0.90),
             ("Z5 Max", 0.90, 1.00)]
    uses = ["easy movement, warm-up & cool-down", "fat-burn base, long easy cardio",
            "comfortably hard — aerobic fitness", "hard intervals, race pace",
            "very short sprints / HIIT peaks"]
    out = []
    for (name, lo, hi), use in zip(spans, uses):
        if resting:
            reserve = hr_max - resting
            out.append({"zone": name, "lo": int(resting + lo * reserve),
                        "hi": int(resting + hi * reserve), "use": use})
        else:
            out.append({"zone": name, "lo": int(lo * hr_max),
                        "hi": int(hi * hr_max), "use": use})
    return out


def mifflin_bmr(weight_kg: float, height_m: float, age: int, gender: str) -> float:
    h_cm = height_m * 100
    base = 10 * weight_kg + 6.25 * h_cm - 5 * age
    return round(base + (5 if gender == "Male" else -161))


def activity_multiplier(days: int) -> float:
    return ACTIVITY_MULTIPLIER.get(days, 1.55)


GOAL_KCAL_DELTA = {"weight_loss": -500, "muscle_gain": 250, "endurance": 150,
                   "general": 0, "flexibility": 0}


def calorie_target(tdee: float, goal: str, gender: str) -> int:
    target = tdee + GOAL_KCAL_DELTA.get(goal, 0)
    floor = 1500 if gender == "Male" else 1200
    return int(round(max(target, floor)))


# Protein g/kg by goal; keto overrides fat; high-protein diet overrides protein.
GOAL_PROTEIN = {"weight_loss": 2.0, "muscle_gain": 1.8, "endurance": 1.6,
                "general": 1.6, "flexibility": 1.4}
GOAL_FAT_PCT = {"weight_loss": 0.30, "muscle_gain": 0.25, "endurance": 0.25,
                "general": 0.30, "flexibility": 0.30}


def macro_split(target_cal: int, weight_kg: float, goal: str, diet: str) -> dict:
    protein_gkg = GOAL_PROTEIN.get(goal, 1.6)
    if diet == "High-Protein":
        protein_gkg = 2.3
    if diet == "Keto":
        protein_gkg = 1.6
    protein_g = protein_gkg * weight_kg
    if diet == "Keto":
        carbs_g = target_cal * 0.07 / 4          # ~7% carbs (<50 g)
        fat_g = (target_cal - protein_g * 4 - carbs_g * 4) / 9
    else:
        fat_g = target_cal * GOAL_FAT_PCT.get(goal, 0.30) / 9
        carbs_g = (target_cal - protein_g * 4 - fat_g * 9) / 4
    protein_cal, carb_cal, fat_cal = protein_g * 4, carbs_g * 4, fat_g * 9
    total = protein_cal + carb_cal + fat_cal
    return {
        "protein_g": round(protein_g), "carbs_g": round(carbs_g),
        "fat_g": round(fat_g),
        "protein_pct": round(100 * protein_cal / total),
        "carbs_pct": round(100 * carb_cal / total),
        "fat_pct": round(100 * fat_cal / total),
        "protein_cal": round(protein_cal), "carbs_cal": round(carb_cal),
        "fat_cal": round(fat_cal),
    }


def water_target(weight_kg: float, session_minutes: int, days: int) -> float:
    """33 ml/kg baseline + ~0.6 L per training hour, averaged across the week."""
    weekly_training_liters = 0.6 * (session_minutes / 60) * days
    return round(weight_kg * 0.033 + weekly_training_liters / 7, 1)


GOAL_INTENSITY = {"weight_loss": (0.65, 0.80), "muscle_gain": (0.60, 0.75),
                  "endurance": (0.55, 0.70), "general": (0.60, 0.78),
                  "flexibility": (0.40, 0.55)}

GOAL_REP_REST = {  # (reps, rest_seconds) by goal for compound lifts
    "weight_loss": ("10–15", 45),
    "muscle_gain": ("6–12", 75),
    "endurance": ("12–20", 30),
    "general": ("8–15", 60),
    "flexibility": ("quality reps", 30),
}


def waist_to_hip_ratio(waist_cm: float, hip_cm: float) -> float:
    return round(waist_cm / hip_cm, 2)


def whr_category(whr: float, gender: str) -> tuple[str, str]:
    """WHO risk thresholds."""
    if gender == "Male":
        if whr < 0.90: return "Low risk", "#72D5AD"
        if whr < 1.00: return "Moderate risk", "#F1C777"
        return "High risk", "#F38BA0"
    if whr < 0.80: return "Low risk", "#72D5AD"
    if whr < 0.85: return "Moderate risk", "#F1C777"
    return "High risk", "#F38BA0"


MET_BY_WORKOUT = {"HIIT": 9.0, "Strength": 6.0, "Cardio": 8.0, "Yoga": 3.0}
ACTIVITY_MULTIPLIER = {1: 1.375, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.55, 6: 1.725, 7: 1.9}

# ---------------------------------------------------------------------------
# Weekly plan generation (rule-based + ML blend)
# ---------------------------------------------------------------------------

from exercise_library import (  # noqa: E402
    EXERCISES,
    WARMUP,
    COOLDOWN,
    MEAL_IDEAS,
    GOAL_LABELS,
    FOCUS_LABELS,
)

SPLITS = {
    1: ["Full Body A"],
    2: ["Full Body A", "Full Body B"],
    3: None,  # resolved per goal/experience below
    4: ["Upper A", "Lower A", "Upper B", "Lower B"],
    5: ["Push", "Pull", "Legs", "Upper", "Lower"],
    6: ["Push", "Pull", "Legs", "Push", "Pull", "Legs"],
    7: ["Push", "Pull", "Legs", "Push", "Pull", "Legs", "Active Recovery"],
}

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]
# Sensible weekday spread per number of days.
_DAY_SLOTS = {1: [0], 2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4],
              5: [0, 1, 2, 3, 4], 6: [0, 1, 2, 3, 4, 5],
              7: [0, 1, 2, 3, 4, 5, 6]}

DAY_PATTERNS = {
    "Full Body A": ["squat", "push", "pull", "core"],
    "Full Body B": ["hinge", "push", "pull", "core"],
    "Full Body C": ["squat", "hinge", "push", "pull", "core"],
    "Push": ["push", "push", "push", "core"],
    "Pull": ["pull", "pull", "pull", "core"],
    "Legs": ["squat", "hinge", "squat", "core"],
    "Upper A": ["push", "pull", "push", "pull", "core"],
    "Upper B": ["pull", "push", "pull", "push", "core"],
    "Lower A": ["squat", "hinge", "squat", "core"],
    "Lower B": ["hinge", "squat", "hinge", "core"],
    "Upper": ["push", "pull", "push", "pull"],
    "Lower": ["squat", "hinge", "squat"],
    "Active Recovery": ["mobility", "mobility", "mobility", "mobility", "mobility"],
}

DAY_TYPE = {name: ("Yoga" if name == "Active Recovery" else "Strength")
            for name in DAY_PATTERNS}
DAY_TYPE["Full Body A"] = "Strength"
DAY_TYPE["Full Body C"] = "Strength"

COMPOUND_PATTERNS = {"push", "pull", "squat", "hinge"}


def _seed(*parts) -> int:
    return zlib.crc32("|".join(str(p) for p in parts).encode())


def resolve_split(days: int, goal: str, experience: int) -> list[str]:
    if days == 3:
        if goal == "muscle_gain" and experience >= 2:
            return ["Push", "Pull", "Legs"]
        return ["Full Body A", "Full Body B", "Full Body C"]
    return list(SPLITS[days])


def _pick_exercises(pattern: str, profile: UserProfile,
                    rng: np.random.Generator) -> list[dict]:
    candidates = [e for e in EXERCISES
                  if e["pattern"] == pattern and e["level"] <= profile.experience]
    if not candidates:  # safety net — relax level constraint
        candidates = [e for e in EXERCISES if e["pattern"] == pattern]
    # Prefer exercises matching the target body focus (when specific).
    if profile.body_focus != "full_body":
        focused = [e for e in candidates
                   if profile.body_focus in e["focus"]]
        others = [e for e in candidates if e not in focused]
        rng.shuffle(focused)
        rng.shuffle(others)
        candidates = focused + others
    else:
        rng.shuffle(candidates)
    return candidates


def generate_day(day_name: str, slot: int, profile: UserProfile) -> dict:
    rng = np.random.default_rng(_seed(day_name, profile.goal, profile.days,
                                      profile.body_focus, profile.experience))
    patterns = DAY_PATTERNS[day_name]
    workout_type = DAY_TYPE[day_name]
    reps, rest = GOAL_REP_REST.get(profile.goal, ("8–15", 60))
    compound_sets = {1: 3, 2: 4, 3: 5}[profile.experience]
    isolation_sets = {1: 2, 2: 3, 3: 4}[profile.experience]

    used, exercises = set(), []
    for pattern in patterns:
        candidates = _pick_exercises(pattern, profile, rng)
        pick = None
        for cand in candidates:
            if cand["name"] not in used:
                pick = cand
                break
        if pick is None:
            pick = candidates[0]
        used.add(pick["name"])
        is_compound = pattern in COMPOUND_PATTERNS
        sets = compound_sets if is_compound else isolation_sets
        if profile.goal == "flexibility":
            scheme = "2 × 60–90s"
        elif is_compound:
            scheme = f"{sets} × {reps}"
        else:
            scheme = f"{sets} × {reps}"
        exercises.append({
            "name": pick["name"],
            "body_part": pick["body_part"],
            "equipment": pick["equipment"],
            "sets_reps": scheme,
            "rest_sec": rest if is_compound else max(rest - 15, 20),
            "cue": pick["cue"],
            "focus_hit": profile.body_focus != "full_body"
                         and profile.body_focus in pick["focus"],
        })

    # Finishers by goal — strength days only, never on Active Recovery
    is_recovery = day_name == "Active Recovery"
    finisher = None
    if not is_recovery:
        if profile.goal == "weight_loss":
            finisher = "10–12 min finisher: 30s battle ropes / 30s rest × 8–10"
        elif profile.goal == "endurance":
            finisher = "15 min Zone-2 cardio (conversational pace)"
        elif profile.goal == "general":
            finisher = "8 min easy cardio + 2 min breathing"

    # Estimated calories: regression+MET blend on the estimated working HR
    lo, hi = GOAL_INTENSITY.get(profile.goal, (0.6, 0.75))
    avg_bpm = predict_avg_bpm(profile, lo, hi)
    hours = profile.session_minutes / 60
    calories = predict_session_calories(profile, workout_type, hours, avg_bpm)
    if finisher and profile.goal in ("weight_loss", "endurance"):
        fin_min = 12 if profile.goal == "weight_loss" else 15
        calories += int(8.0 * profile.weight_kg * fin_min / 60)

    zone = {"weight_loss": "Z3–Z4 (Tempo→Threshold)",
            "muscle_gain": "Z2–Z3 (Endurance→Tempo)",
            "endurance": "Z2 (Endurance)",
            "general": "Z2–Z4 mix",
            "flexibility": "Z1–Z2 (Recovery→Endurance)"}.get(profile.goal, "Z2–Z3")

    return {
        "weekday": WEEKDAYS[slot],
        "name": day_name,
        "type": workout_type,
        "exercises": exercises,
        "warmup": list(WARMUP),
        "cooldown": list(COOLDOWN),
        "finisher": finisher,
        "est_calories": calories,
        "avg_bpm": int(avg_bpm),
        "target_zone": zone,
    }


def build_week(profile: UserProfile) -> list[dict]:
    days = resolve_split(profile.days, profile.goal, profile.experience)
    slots = _DAY_SLOTS[profile.days]
    return [generate_day(name, slot, profile)
            for name, slot in zip(days, slots)]


def nutrition_summary(profile: UserProfile) -> dict:
    bmr = mifflin_bmr(profile.weight_kg, profile.height_m,
                      profile.age, profile.gender)
    tdee = bmr * activity_multiplier(profile.days)
    target = calorie_target(tdee, profile.goal, profile.gender)
    comparison = None
    if profile.known_calories:
        delta = target - profile.known_calories
        comparison = {"known": int(profile.known_calories), "delta": int(delta)}
    macros = macro_split(target, profile.weight_kg, profile.goal, profile.diet)
    water = water_target(profile.weight_kg, profile.session_minutes, profile.days)
    return {"bmr": int(round(bmr)), "tdee": int(round(tdee)),
            "target": target, "comparison": comparison,
            "macros": macros, "water": water,
            "meal_ideas": MEAL_IDEAS.get(profile.diet, MEAL_IDEAS["Omnivore"])}


def recovery_tips(profile: UserProfile) -> dict:
    sleep = {1: "8–9 hours", 2: "7–9 hours", 3: "7–9 hours + deload"}[profile.experience]
    rest_days = 7 - profile.days
    tips = [
        f"Sleep {sleep} — growth hormone peaks during deep sleep; it is when adaptation happens.",
        f"Keep {rest_days} rest day(s)/week; light walking is encouraged — movement aids recovery.",
        "Spread protein across 4 meals (~0.4 g/kg per meal) to maximise muscle protein synthesis.",
        "5 min of static stretching per muscle group after every session, plus one mobility day if flexible-goal.",
        "Manage stress — chronic cortisol blunts recovery; 10 min breathing / nature / sunlight daily.",
    ]
    if profile.experience >= 2:
        tips.append("Deload every 4–6 weeks: halve the volume (sets) while keeping intensity moderate.")
    if profile.experience == 3:
        tips.append("Track HRV or resting HR each morning — two suppressed readings in a row = extra rest day.")
    tips.append("Creatine monohydrate 3–5 g/day is the most researched ergogenic aid; discuss with your physician if you have kidney issues.")
    return {"sleep": sleep, "rest_days": rest_days, "tips": tips}


def body_metrics(profile: UserProfile) -> dict:
    b = bmi(profile.weight_kg, profile.height_m)
    cat, color = bmi_category(b)
    whr = waist_to_hip_ratio(profile.waist_cm, profile.hip_cm)
    whr_cat, whr_color = whr_category(whr, profile.gender)
    fat = profile.body_fat_pct if profile.body_fat_pct is not None \
        else estimate_body_fat(b, profile.age, profile.gender)
    fat_source = "measured" if profile.body_fat_pct is not None else "estimated (Deurenberg)"
    ideal_lo, ideal_hi = 18.5 * profile.height_m**2, 24.9 * profile.height_m**2
    return {"bmi": b, "bmi_cat": cat, "bmi_color": color,
            "whr": whr, "whr_cat": whr_cat, "whr_color": whr_color,
            "body_fat": fat, "fat_source": fat_source,
            "ideal_range": (round(ideal_lo, 1), round(ideal_hi, 1))}


def weekly_projection(profile: UserProfile, target_cal: int) -> dict:
    """Crude 12-week body-mass projection with honest caveats."""
    if profile.goal == "weight_loss":
        deficit = 500
        kg = deficit * 7 * 12 / 7700
        return {"headline": f"≈ −{kg:.1f} kg fat mass in 12 weeks",
                "detail": "Assumes a consistent 500 kcal/day deficit and tracking. "
                          "Rate slows as body mass drops — recalculate every 4–6 weeks."}
    if profile.goal == "muscle_gain":
        return {"headline": "≈ +0.5 to +1.5 kg lean mass in 12 weeks",
                "detail": "Novice–intermediate rate with progressive overload and a "
                          "250 kcal surplus. Actual depends on genetics, sleep and consistency."}
    return {"headline": "Weight-stable performance focus",
            "detail": "Maintenance calories with quality training — expect body "
                      "recomposition rather than scale changes."}


def build_plan(profile: UserProfile) -> dict:
    """Bundle everything the UI and PDF need into one plain dict."""
    persona_model = get_persona_model()
    persona_id = persona_model.predict(profile)
    hr_max = estimate_hr_max(profile.age)
    zones = hr_zones(hr_max, profile.resting_hr)
    metrics = body_metrics(profile)
    nutrition = nutrition_summary(profile)
    days = build_week(profile)
    weekly_cal = sum(d["est_calories"] for d in days)
    _, cal_report = train_calorie_model()
    return {
        "profile": profile,
        "persona_id": persona_id,
        "persona_name": persona_model.persona_names[persona_id],
        "persona_desc": persona_model.persona_desc[persona_id],
        "persona_size": persona_model.size(persona_id),
        "persona_centroid": persona_model.centroid(persona_id).to_dict(),
        "hr_max": hr_max,
        "zones": zones,
        "metrics": metrics,
        "nutrition": nutrition,
        "week": days,
        "weekly_calories": weekly_cal,
        "calorie_model": cal_report,
        "recovery": recovery_tips(profile),
        "projection": weekly_projection(profile, nutrition["target"]),
        "goal_label": GOAL_LABELS.get(profile.goal, profile.goal),
        "focus_label": FOCUS_LABELS.get(profile.body_focus, profile.body_focus),
    }


DISCLAIMER = (
    "This plan is general fitness guidance generated from population averages — it is NOT "
    "medical advice. Consult a physician before starting, especially with cardiovascular "
    "disease, hypertension, diabetes, pregnancy or musculoskeletal issues. Stop any exercise "
    "that causes pain (not to be confused with normal exertion). Nutrition targets are "
    "estimates; adjust to your response and consult a registered dietitian for clinical needs."
)
