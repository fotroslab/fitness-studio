"""Generate a synthetic gym-members dataset with *known* personas.

Why this exists
---------------
The real Kaggle dataset (``gym_members_exercise_tracking.csv``, 973 rows) is
fairly continuous — natural clusters are weak (best silhouette ≈ 0.28), which
is honest but hard to *demonstrate* segmentation on. This generator produces a
companion dataset where ten distinct fitness personas are baked into the data
generating process, so a clustering pipeline can be shown recovering real
structure (and scored against ground truth with the Adjusted Rand Index).

Ten personas
------------
1.  **HIIT Warrior**    — young, very frequent (4–5 d/wk), HIIT, high calories,
    lean, high average heart rate.
2.  **Power Builder**   — strength training, higher BMI, moderate frequency,
    moderate calories.
3.  **Cardio Runner**   — long cardio sessions, high calories, mid BMI.
4.  **Mindful Mover**   — yoga, older, low intensity, low calories, low BMI.
5.  **Casual Beginner** — low frequency (2 d/wk), beginner, mixed workouts,
    low calories.
6.  **Weekend Warrior** — only 2–3 sessions per week but *long* ones; high
    calorie burn crammed into few days.
7.  **Fat-Loss Focused**— higher BMI/fat, high frequency (4 d/wk), mixed
    cardio+strength, calorie-burn oriented.
8.  **Plateau Veteran** — expert, 4–5 d/wk, moderate everything; years of
    experience with stalled progress — needs program change, not more of the
    same.
9.  **MetCon Addict**   — 19–30, maximum relative intensity (high HRR),
    trains almost daily; lowest body fat in the gym.
10. **Senior Wellness** — 50+, low intensity, 2–3 d/wk, health-focused
    cardio/yoga; lowest max heart rate (physiological: ~208 − 0.7×age).

Heart-rate physiology is modelled: max HR falls with age, avg HR < max HR,
resting HR < avg HR, and athletes rest lower.

The output keeps the exact 15-column schema of the real dataset and adds a
``Persona`` ground-truth column (the app drops it from the modelling matrix
automatically).

Usage
-----
    python generate_data.py            # writes data/gym_members_synthetic.csv
    python generate_data.py 973 42     # n_rows, seed
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

# Persona blueprints. Ranges are calibrated to the real dataset's observed
# min/max where possible, with the *joint* distributions differing enough for
# clusters to be recoverable.
PERSONAS = {
    "HIIT Warrior": dict(
        share=0.11, age=(22, 38), bmi=(20, 26), fat=(12, 20),
        calories=(1100, 1600), freq=(4, 5), exp=(2, 3), avg_bpm=(150, 168),
        session=(1.2, 1.8), workout="HIIT",
    ),
    "Power Builder": dict(
        share=0.11, age=(24, 45), bmi=(26, 34), fat=(22, 32),
        calories=(700, 1000), freq=(3, 4), exp=(2, 3), avg_bpm=(130, 150),
        session=(0.8, 1.3), workout="Strength",
    ),
    "Cardio Runner": dict(
        share=0.11, age=(26, 50), bmi=(21, 28), fat=(16, 26),
        calories=(1000, 1400), freq=(3, 5), exp=(1, 3), avg_bpm=(145, 166),
        session=(1.3, 2.0), workout="Cardio",
    ),
    "Mindful Mover": dict(
        share=0.10, age=(35, 59), bmi=(19, 25), fat=(18, 28),
        calories=(450, 750), freq=(2, 4), exp=(1, 3), avg_bpm=(120, 139),
        session=(0.8, 1.5), workout="Yoga",
    ),
    "Casual Beginner": dict(
        share=0.10, age=(20, 55), bmi=(24, 32), fat=(24, 35),
        calories=(400, 700), freq=(2, 2), exp=(1, 1), avg_bpm=(125, 145),
        session=(0.5, 1.0), workout=None,  # mixed
    ),
    "Weekend Warrior": dict(
        share=0.10, age=(25, 45), bmi=(23, 30), fat=(18, 28),
        calories=(900, 1350), freq=(2, 3), exp=(1, 2), avg_bpm=(140, 158),
        session=(1.6, 2.0), workout=None,  # mixed cardio/strength
    ),
    "Fat-Loss Focused": dict(
        share=0.10, age=(30, 55), bmi=(27, 35), fat=(28, 37),
        calories=(900, 1250), freq=(4, 4), exp=(1, 2), avg_bpm=(132, 150),
        session=(1.0, 1.5), workout=None,  # cardio + strength mix
    ),
    "Plateau Veteran": dict(
        share=0.09, age=(35, 55), bmi=(23, 29), fat=(20, 28),
        calories=(700, 950), freq=(4, 5), exp=(3, 3), avg_bpm=(135, 152),
        session=(0.9, 1.3), workout=None,  # knows the gym too well
    ),
    "MetCon Addict": dict(
        share=0.09, age=(19, 30), bmi=(19, 25), fat=(10, 17),
        calories=(1200, 1680), freq=(5, 5), exp=(2, 3), avg_bpm=(155, 171),
        session=(1.0, 1.6), workout="HIIT",
    ),
    "Senior Wellness": dict(
        share=0.09, age=(52, 66), bmi=(22, 30), fat=(24, 34),
        calories=(380, 650), freq=(2, 3), exp=(1, 2), avg_bpm=(118, 136),
        session=(0.6, 1.1), workout="Yoga",  # + light cardio, mixed below
    ),
}

WORKOUT_TYPES = ["Cardio", "Strength", "Yoga", "HIIT"]
LOW_IMPACT = ["Yoga", "Cardio"]  # Senior Wellness / Mindful Mover mix


def _draw(rng: np.random.Generator, lo: float, hi: float, n: int) -> np.ndarray:
    """Truncated-normal draw centred in [lo, hi] — more realistic than uniform."""
    mu, sigma = (lo + hi) / 2, (hi - lo) / 5
    return np.clip(rng.normal(mu, sigma, n), lo, hi)


def generate(n_rows: int = 973, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    names = list(PERSONAS)
    shares = np.array([PERSONAS[n]["share"] for n in names])
    shares = shares / shares.sum()
    persona_labels = rng.choice(names, size=n_rows, p=shares)

    rows = []
    for label in persona_labels:
        p = PERSONAS[label]
        age = int(_draw(rng, *p["age"], 1)[0])
        bmi = float(_draw(rng, *p["bmi"], 1)[0])
        height = float(_draw(rng, 1.50, 2.00, 1)[0])
        weight = bmi * height**2
        avg_bpm = int(_draw(rng, *p["avg_bpm"], 1)[0])
        # Physiology: max HR ≈ 208 − 0.7 × age, with person-level noise.
        age_max = 208 - 0.7 * age
        max_bpm = int(np.clip(age_max + rng.normal(0, 4), avg_bpm + 12, 199))
        # Fit athletes rest lower.
        athlete = label in ("HIIT Warrior", "MetCon Addict", "Cardio Runner")
        resting = int(np.clip(avg_bpm - rng.integers(70 if athlete else 55,
                                                     95), 50, 74))
        session = float(_draw(rng, *p["session"], 1)[0])
        calories = float(_draw(rng, *p["calories"], 1)[0])
        # Calories scale with session length (real data r≈0.9).
        calories = float(np.clip(calories * (0.7 + 0.3 * session), 303, 1783))
        fat = float(_draw(rng, *p["fat"], 1)[0])
        water = float(np.clip(1.5 + 0.9 * session + rng.normal(0, 0.35), 1.5, 3.7))
        freq = int(rng.integers(p["freq"][0], p["freq"][1] + 1))
        exp = int(rng.integers(p["exp"][0], p["exp"][1] + 1))
        if p["workout"]:
            workout = p["workout"]
        elif label == "Senior Wellness":
            workout = rng.choice(LOW_IMPACT, p=[0.55, 0.45])
        else:
            workout = rng.choice(WORKOUT_TYPES)
        rows.append(
            dict(
                Age=age,
                Gender=rng.choice(["Male", "Female"]),
                **{"Weight (kg)": round(weight, 1)},
                **{"Height (m)": round(height, 2)},
                Max_BPM=max_bpm,
                Avg_BPM=avg_bpm,
                Resting_BPM=resting,
                **{"Session_Duration (hours)": round(session, 2)},
                Calories_Burned=round(calories, 0),
                Workout_Type=workout,
                Fat_Percentage=round(fat, 1),
                **{"Water_Intake (liters)": round(water, 1)},
                **{"Workout_Frequency (days/week)": freq},
                Experience_Level=exp,
                BMI=round(bmi, 2),
                Persona=label,
            )
        )

    df = pd.DataFrame(rows).sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


def main() -> None:
    n_rows = int(sys.argv[1]) if len(sys.argv) > 1 else 973
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "gym_members_synthetic.csv"
    df = generate(n_rows, seed)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows -> {out}")
    print(df["Persona"].value_counts().to_string())


if __name__ == "__main__":
    main()
