"""Personalized Workout & Nutrition Recommender
===============================================
A standalone Streamlit application that assigns a gym member to a data-driven
fitness persona (K-Means on the real Kaggle Gym Members Exercise Dataset) and
generates a complete, actionable program: weekly split with exercises, sets/
reps, HR zones and calorie estimates, plus nutrition targets (BMR/TDEE,
macros, hydration) and recovery guidance. Downloadable as a PDF.

Run:
    streamlit run workout_recommender_app.py

Architecture:
    exercise_library.py   — exercise/movement database (patterns, levels, cues)
    recommendation_engine.py — persona model + physiology + plan generation
    pdf_report.py         — PDF plan builder (fpdf2)
    this file             — wizard UI (3 steps) + 4 result tabs
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import theme  # noqa: E402
import recommendation_engine as engine  # noqa: E402
from exercise_library import EXERCISES, GOAL_LABELS, FOCUS_LABELS  # noqa: E402
from pdf_report import build_plan_pdf  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent / "data" / "gym_members_exercise_tracking.csv"

ACCENT = theme.PALETTE["accent"]
GOOD, WARN, BAD = theme.PALETTE["good"], theme.PALETTE["warn"], theme.PALETTE["bad"]


@st.cache_data(show_spinner=False)
def raw_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


@st.cache_resource(show_spinner=False)
def persona_model():
    return engine.get_persona_model()


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def init_state():
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("plan", None)
    st.session_state.setdefault("pdf_bytes", None)


def goto(step: int):
    st.session_state["step"] = step


def generate(profile: engine.UserProfile):
    with st.spinner("Assigning persona & building your plan…"):
        plan = engine.build_plan(profile)
        st.session_state["plan"] = plan
        try:
            st.session_state["pdf_bytes"] = build_plan_pdf(plan)
            st.session_state["pdf_error"] = None
        except RuntimeError as exc:  # fpdf2 missing — app must still work
            st.session_state["pdf_bytes"] = None
            st.session_state["pdf_error"] = str(exc)
    goto(4)


def reset_all():
    st.session_state["plan"] = None
    st.session_state["pdf_bytes"] = None
    goto(1)


# ---------------------------------------------------------------------------
# Wizard UI
# ---------------------------------------------------------------------------

def stepper():
    labels = ["1 · Body & Measurements", "2 · Profile & Goals", "3 · Lifestyle & Nutrition"]
    cols = st.columns(3)
    for i, (col, label) in enumerate(zip(cols, labels), start=1):
        current = st.session_state["step"] == i or (i == 4 and st.session_state["step"] == 4)
        done = st.session_state["step"] > i
        style = (
            f"border:1px solid {ACCENT}; color:{ACCENT}; box-shadow:0 0 12px rgba(94,224,181,.25);"
            if current else
            f"border:1px solid {theme.PALETTE['border']}; color:{theme.PALETTE['muted']};"
            if not done else
            f"border:1px solid {GOOD}; color:{GOOD};"
        )
        col.markdown(
            f'<div style="{style} border-radius:10px; padding:.5rem .8rem; text-align:center; '
            f'font-size:.85rem; font-weight:600; background:{theme.PALETTE["panel"]};">'
            f'{"✓ " if done else ""}{label}</div>',
            unsafe_allow_html=True,
        )


def imported(key, default):
    return st.session_state.get("imported_profile", {}).get(key, default)


def step_body():
    theme.section("🧍", "Step 1 — Basic demographics & body metrics")
    c1, c2, c3 = st.columns(3)
    age = c1.number_input("Age (years)", 16, 80, imported("age", 28))
    gender = c2.selectbox("Gender", ["Male", "Female"], index=["Male", "Female"].index(imported("gender", "Male")))
    height_m = c3.number_input("Height (m)", 1.40, 2.10, imported("height_m", 1.75), step=0.01, format="%.2f")
    weight_kg = c1.number_input("Weight (kg)", 40.0, 180.0, imported("weight_kg", 78.0), step=0.5)

    st.caption("📏 Body measurements (optional but make the insights much richer)")
    m1, m2, m3, m4, m5 = st.columns(5)
    arm = m1.number_input("Arm (cm)", 20.0, 55.0, 33.0, step=0.5)
    waist = m2.number_input("Waist (cm)", 55.0, 140.0, 82.0, step=0.5)
    thigh = m3.number_input("Thigh (cm)", 35.0, 80.0, 55.0, step=0.5)
    hip = m4.number_input("Hip (cm)", 70.0, 140.0, 98.0, step=0.5)
    chest = m5.number_input("Chest (cm)", 70.0, 150.0, 98.0, step=0.5)

    know_bf = st.checkbox("I know my body-fat %", value=imported("body_fat_pct", None) is not None)
    body_fat = None
    if know_bf:
        body_fat = st.number_input("Body fat %", 5.0, 50.0, imported("body_fat_pct", 18.0), step=0.5)
    else:
        st.caption("No problem — we'll estimate it with the Deurenberg equation "
                   "(BMI + age + sex).")

    bmi_val = engine.bmi(weight_kg, height_m)
    cat, color = engine.bmi_category(bmi_val)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="ds-card"><div class="ds-metric-label">Live BMI preview</div>'
                f'<div class="ds-metric-value" style="color:{color};">{bmi_val}</div>'
                f'<div class="ds-metric-sub">{cat}</div></div>',
                unsafe_allow_html=True)
    c2.markdown(f'<div class="ds-card"><div class="ds-metric-label">Height</div>'
                f'<div class="ds-metric-value">{height_m:.2f} m</div></div>',
                unsafe_allow_html=True)
    c3.markdown(f'<div class="ds-card"><div class="ds-metric-label">Weight</div>'
                f'<div class="ds-metric-value">{weight_kg:.1f} kg</div></div>',
                unsafe_allow_html=True)

    if st.button("Next: Profile & Goals →", type="primary"):
        st.session_state["step1"] = dict(age=age, gender=gender, height_m=height_m,
                                         weight_kg=weight_kg, arm_cm=arm, waist_cm=waist,
                                         thigh_cm=thigh, hip_cm=hip, chest_cm=chest,
                                         body_fat_pct=body_fat)
        goto(2)
        st.rerun()


def step_profile():
    theme.section("🎯", "Step 2 — Fitness profile & goals")
    c1, c2 = st.columns(2)
    experience_label = c1.selectbox("Experience level",
                                    ["Beginner (< 1 year)", "Intermediate (1–3 years)",
                                     "Advanced (3+ years)"], index=imported("experience", 2)-1)
    experience = ["Beginner", "Intermediate", "Advanced"].index(
        experience_label.split(" ")[0]) + 1
    goal = c2.selectbox("Primary goal",
                        ["Weight Loss", "Muscle Gain", "Endurance",
                         "General Fitness", "Flexibility"])
    goal_key = {v: k for k, v in GOAL_LABELS.items()}[goal]

    focus = st.selectbox("Target body focus",
                         ["Full Body", "Upper Body", "Lower Body",
                          "Core / Abs", "Glutes & Legs"])
    focus_key = {v: k for k, v in FOCUS_LABELS.items()}[focus]

    c3, c4 = st.columns(2)
    days = c3.slider("Workout days available per week", 1, 7, 4)
    session_minutes = c4.slider("Session duration preference (min)", 30, 120, 60, step=5)

    know_hr = st.checkbox("I know my resting heart rate (improves HR zones — Karvonen method)", value=imported("resting_hr", None) is not None)
    resting_hr = None
    if know_hr:
        resting_hr = st.slider("Resting HR (bpm)", 42, 95, imported("resting_hr", 62))

    col_back, col_next = st.columns([1, 4])
    if col_back.button("← Back"):
        goto(1)
        st.rerun()
    if col_next.button("Next: Lifestyle & Nutrition →", type="primary"):
        st.session_state["step2"] = dict(experience=experience, goal=goal_key,
                                         body_focus=focus_key, days=days,
                                         session_minutes=session_minutes,
                                         resting_hr=resting_hr)
        goto(3)
        st.rerun()


def step_lifestyle():
    theme.section("🥗", "Step 3 — Lifestyle & nutrition")
    c1, c2 = st.columns(2)
    diet = c1.selectbox("Dietary preference",
                        ["Omnivore", "Vegetarian", "Vegan", "Keto", "High-Protein"])
    water = c2.slider("Daily water intake (liters)", 1.0, 6.0, imported("water_liters", 2.5), step=0.1)

    know_cal = st.checkbox("I know my current daily calorie intake")
    known_calories = None
    if know_cal:
        known_calories = st.slider("Current daily intake (kcal)", 1200, 4500, 2500, step=50)
    else:
        st.caption("We'll estimate your TDEE from BMR (Mifflin-St Jeor) × activity.")

    st.info("Ready? Your plan is built from 973 real gym sessions + physiology models. "
            "Generation takes a couple of seconds.", icon="🚀")

    col_back, col_go = st.columns([1, 4])
    if col_back.button("← Back"):
        goto(2)
        st.rerun()
    if col_go.button("🚀 Generate my plan", type="primary"):
        s1, s2 = st.session_state.get("step1"), st.session_state.get("step2")
        if not s1 or not s2:
            st.warning("Please complete steps 1 and 2 first.")
            goto(1)
            st.rerun()
        profile = engine.UserProfile(
            age=s1["age"], gender=s1["gender"], height_m=s1["height_m"],
            weight_kg=s1["weight_kg"], arm_cm=s1["arm_cm"], waist_cm=s1["waist_cm"],
            thigh_cm=s1["thigh_cm"], hip_cm=s1["hip_cm"], chest_cm=s1["chest_cm"],
            body_fat_pct=s1["body_fat_pct"],
            experience=s2["experience"], goal=s2["goal"], body_focus=s2["body_focus"],
            days=s2["days"], session_minutes=s2["session_minutes"],
            resting_hr=s2["resting_hr"],
            diet=diet, known_calories=known_calories, water_liters=water,
        )
        generate(profile)
        st.rerun()


# ---------------------------------------------------------------------------
# Result tabs
# ---------------------------------------------------------------------------

def tab_persona(plan):
    theme.section("🎭", f"You are a **{plan['persona_name']}**")
    p = plan["profile"]
    m = plan["metrics"]

    c1, c2 = st.columns([2, 1])
    with c1:
        theme.persona_card(
            f"{plan['persona_name']}",
            f"Cluster {plan['persona_id']} · ~{plan['persona_size']} of 973 members "
            f"({plan['persona_size'] / 973:.0%} of the gym) · trained K-Means persona model",
            f"{plan['persona_desc']}<br><br><b>Why you got this label:</b> your metrics "
            f"(age {p.age}, BMI {m['bmi']}, ~{plan['week'][0]['avg_bpm']} bpm working HR, "
            f"{p.days} sessions/week, level {p.experience}/3) sit closest to this persona's "
            f"centroid in the model trained on the real gym dataset.",
            ACCENT)
        st.caption(
            "Persona model: K-Means (k=4) on Age, BMI, Body-fat %, Frequency, "
            "Experience, Preferred session length — features a user can actually provide. "
            "Persona assignment drives plan intensity, not medical judgement.")
    with c2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=m["bmi"],
            title={"text": "BMI", "font": {"color": theme.PALETTE["text"]}},
            gauge={
                "axis": {"range": [12, 45], "tickcolor": theme.PALETTE["muted"]},
                "bar": {"color": ACCENT},
                "steps": [
                    {"range": [12, 18.5], "color": "#223"},
                    {"range": [18.5, 25], "color": "#123"},
                    {"range": [25, 30], "color": "#332"},
                    {"range": [30, 45], "color": "#322"},
                ],
                "threshold": {"line": {"color": WARN, "width": 3}, "value": 25},
            },
        ))
        theme.style_fig(fig, 210)
        st.plotly_chart(fig, width="stretch")
        st.markdown(f"**{m['bmi_cat']}** · body fat {m['body_fat']}% ({m['fat_source']})")

    # Radar: user vs persona centroid, percentile-scaled against the dataset.
    theme.section("📡", "You vs. your persona's centroid")
    df = raw_dataset()
    fat_meas = p.body_fat_pct if p.body_fat_pct is not None else m["body_fat"]
    axes = ["Age", "BMI", "Fat_Percentage", "Workout_Frequency (days/week)",
            "Experience_Level", "Session_Duration (hours)"]
    labels = ["Age", "BMI", "Body fat %", "Freq (d/wk)", "Experience", "Session (h)"]
    user_vals = [p.age, m["bmi"], fat_meas, p.days, p.experience,
                 p.session_minutes / 60]

    def pct(col, v):
        return float((df[col] < v).mean() * 100)

    centroid = plan["persona_centroid"]
    user_pct = [pct(c, v) for c, v in zip(axes, user_vals)]
    cent_pct = [pct(c, centroid[c]) for c in axes]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=user_pct + user_pct[:1],
                                  theta=labels + labels[:1], fill="toself",
                                  name="You", line=dict(color=ACCENT, width=2)))
    fig.add_trace(go.Scatterpolar(r=cent_pct + cent_pct[:1],
                                  theta=labels + labels[:1], fill="toself",
                                  name=plan["persona_name"],
                                  line=dict(color=theme.PALETTE["accent2"], width=2)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100],
                                                 ticksuffix="th")),
                      title="Percentile profile (0–100 vs the gym population)")
    theme.style_fig(fig, 420)
    st.plotly_chart(fig, width="stretch")

    with st.expander("🧾 Your inputs (snapshot)"):
        snapshot = ["Age", "Gender", "Height", "Weight", "Arm", "Waist", "Thigh",
                    "Hip", "Chest", "Body fat", "Experience (1–3)", "Goal",
                    "Body focus", "Days/week", "Session", "Resting HR", "Diet",
                    "Water"]
        values = [str(p.age), p.gender, f"{p.height_m:.2f} m", f"{p.weight_kg} kg",
                  f"{p.arm_cm} cm", f"{p.waist_cm} cm", f"{p.thigh_cm} cm",
                  f"{p.hip_cm} cm", f"{p.chest_cm} cm",
                  f"{fat_meas}%", str(p.experience), plan["goal_label"],
                  plan["focus_label"], str(p.days), f"{p.session_minutes} min",
                  str(p.resting_hr) if p.resting_hr else "—", p.diet,
                  f"{p.water_liters} L"]
        st.dataframe(pd.DataFrame({"Field": snapshot, "Value": values}),
                     width="stretch", hide_index=True)


def tab_workout(plan):
    week = plan["week"]
    theme.section("📅", "Your weekly split")
    total = plan["weekly_calories"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions / week", len(week))
    c2.metric("Est. weekly burn", f"{total:,} kcal")
    c3.metric("Total volume", f"{len(week) * plan['profile'].session_minutes / 60:.1f} h")
    c4.metric("Target intensity", plan["week"][0]["target_zone"].split(" (")[0])

    fig = px.bar(pd.DataFrame({"Day": [d["weekday"] for d in week],
                               "Est. kcal": [d["est_calories"] for d in week]}),
                 x="Day", y="Est. kcal", color="Day", text="Est. kcal",
                 color_discrete_sequence=theme.CLUSTER_COLORS,
                 title="Estimated calories per session")
    theme.style_fig(fig, 300)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

    for d in week:
        with st.expander(f"{d['weekday']} — {d['name']} · {d['type']} · "
                         f"~{d['est_calories']} kcal · HR {d['target_zone']}",
                         expanded=False):
            ex_df = pd.DataFrame([{
                "#": i + 1,
                "Exercise": e["name"] + (" ★" if e["focus_hit"] else ""),
                "Sets × Reps": e["sets_reps"],
                "Rest": f"{e['rest_sec']}s",
                "Equipment": e["equipment"],
                "Coaching cue": e["cue"],
            } for i, e in enumerate(d["exercises"])])
            st.dataframe(ex_df, width="stretch", hide_index=True)
            st.caption("★ = matches your target body focus. "
                       f"Estimated working HR ≈ {d['avg_bpm']} bpm "
                       f"({d['target_zone']}).")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Warm-up (do this — non-negotiable)**")
                for w in d["warmup"]:
                    st.markdown(f"- {w}")
            with c2:
                st.markdown("**Cool-down & recovery**")
                for cd in d["cooldown"]:
                    st.markdown(f"- {cd}")
            if d["finisher"]:
                st.markdown(f"**Finisher:** {d['finisher']}")
    st.caption("Calorie estimates blend a Gradient-Boosted model trained on the dataset "
               f"(R² = {plan['calorie_model']['r2']}, MAE = {plan['calorie_model']['mae']} kcal) "
               "with the MET equation — see Progress & Insights for the honesty box.")


def tab_nutrition(plan):
    n = plan["nutrition"]
    mac = n["macros"]
    p = plan["profile"]

    theme.section("🔥", "Energy balance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMR (Mifflin-St Jeor)", f"{n['bmr']:,} kcal")
    c2.metric("TDEE (activity-adjusted)", f"{n['tdee']:,} kcal")
    c3.metric("Daily target", f"{n['target']:,} kcal",
              delta=f"{n['target'] - n['tdee']:+,} vs TDEE")
    if n["comparison"]:
        c4.metric("vs. your intake", f"{n['comparison']['known']:,} kcal",
                  delta=f"{n['comparison']['delta']:+,} kcal/day")
    else:
        c4.metric("Your intake", "not provided")

    theme.insight(
        f"Goal delta applied: <b>{GOAL_LABELS.get(p.goal, p.goal)}</b> → "
        f"{'−500 kcal/day deficit' if p.goal == 'weight_loss' else '+250 kcal/day surplus' if p.goal == 'muscle_gain' else 'maintenance'}. "
        "Targets are population estimates — adjust by 100–200 kcal based on 2–3 weeks of scale + mirror feedback.")

    theme.section("🥩", "Macro split (per day)")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(values=[mac["protein_g"], mac["carbs_g"], mac["fat_g"]],
                     names=[f"Protein {mac['protein_g']}g", f"Carbs {mac['carbs_g']}g",
                            f"Fat {mac['fat_g']}g"],
                     hole=0.55, color_discrete_sequence=[ACCENT, theme.PALETTE["accent2"], GOOD],
                     title=f"Grams of each macro ({n['target']:,} kcal)")
        theme.style_fig(fig, 340)
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = go.Figure(go.Bar(
            x=[mac["protein_g"], mac["carbs_g"], mac["fat_g"]],
            y=["Protein", "Carbs", "Fat"],
            orientation="h",
            marker_color=[ACCENT, theme.PALETTE["accent2"], GOOD],
            text=[f"{mac['protein_g']} g ({mac['protein_pct']}%)",
                  f"{mac['carbs_g']} g ({mac['carbs_pct']}%)",
                  f"{mac['fat_g']} g ({mac['fat_pct']}%)"],
            textposition="outside"))
        fig.update_layout(title="Macro targets (g/day)", xaxis_title="grams")
        theme.style_fig(fig, 340)
        st.plotly_chart(fig, width="stretch")

    if p.diet == "Keto":
        theme.insight("<b>Keto mode:</b> carbs capped at ~7% of calories. "
                      "Electrolytes and 2–3 L water matter — expect a fast scale drop in week 1–2 (glycogen + water), not fat.")
    elif p.diet in ("Vegan", "Vegetarian"):
        theme.insight("<b>Plant-based:</b> pair complementary proteins (lentil + rice, "
                      "soy + grains) across the day; consider B12, iron and omega-3 (algae oil) — discuss with your physician.")

    theme.section("💧", "Hydration")
    target_water = n["water"]
    c1, c2 = st.columns([1, 2])
    with c1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=target_water,
            number={"suffix": " L"},
            title={"text": "Water target", "font": {"color": theme.PALETTE["text"]}},
            gauge={"axis": {"range": [0, 6]},
                   "bar": {"color": ACCENT},
                   "steps": [{"range": [0, 2], "color": "#332"},
                             {"range": [2, 3.5], "color": "#123"},
                             {"range": [3.5, 6], "color": "#223"}]}))
        theme.style_fig(fig, 200)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown(f"**Your current intake:** {p.water_liters} L/day → "
                    f"**target:** {target_water} L/day "
                    f"(+{max(0, target_water - p.water_liters):.1f} L)")
        st.markdown("- 500 ml on waking · 500 ml pre-workout · 1 L spread across the session · "
                    "500 ml post-workout\n"
                    "- Pale-yellow urine = well hydrated; dark = drink now\n"
                    "- +0.5–1 L on days over 60 min or in heat")

    theme.section("🍽️", "Meals that fit your diet")
    cols = st.columns(5)
    for i, (col, idea) in enumerate(zip(cols * 3, n["meal_ideas"])):
        col.markdown(f'<div class="ds-card" style="min-height:84px;"><div class="ds-metric-sub">'
                     f'Option {i + 1}</div>{idea}</div>', unsafe_allow_html=True)

    with st.expander("⏰ Meal timing around training"):
        st.markdown(
            "- **Pre (1–2h before):** carbs + moderate protein, low fat/fibre — e.g. oats + whey, banana + toast\n"
            "- **Intra (if > 75 min):** sip 30–60 g carbs/hour + electrolytes\n"
            "- **Post (within 2h):** 0.4 g/kg protein + 0.8–1 g/kg carbs — e.g. chicken + rice, skyr + granola\n"
            "- **Pre-sleep:** casein or skyr — slow protein overnight supports recovery")

    theme.section("🛌", "Recovery protocol")
    rec = plan["recovery"]
    c1, c2 = st.columns(2)
    c1.metric("Sleep target", rec["sleep"])
    c2.metric("Rest days / week", rec["rest_days"])
    for tip in rec["tips"]:
        st.markdown(f"- {tip}")


def tab_progress(plan):
    p = plan["profile"]
    m = plan["metrics"]
    n = plan["nutrition"]
    week = plan["week"]

    theme.section("📈", "What 12 weeks could look like")
    st.markdown(
        f'<div class="ds-persona" style="--pc: {ACCENT};"><h4>'
        f'{plan["projection"]["headline"]}</h4><p>{plan["projection"]["detail"]}</p></div>',
        unsafe_allow_html=True)

    theme.section("🔥", "Weekly energy expenditure (cumulative)")
    days_x = [d["weekday"] for d in week]
    cum = np.cumsum([d["est_calories"] for d in week])
    fig = go.Figure(go.Scatter(x=days_x, y=cum, mode="lines+markers",
                               line=dict(color=ACCENT, width=3),
                               fill="tozeroy", fillcolor="rgba(94,224,181,.08)"))
    fig.update_layout(title="Cumulative estimated calories burned across the week",
                      yaxis_title="cumulative kcal")
    theme.style_fig(fig, 320)
    st.plotly_chart(fig, width="stretch")

    theme.section("🧬", "Body-composition dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BMI", m["bmi"], help=m["bmi_cat"])
    c2.metric("Body fat", f"{m['body_fat']}%", help=m["fat_source"])
    c3.metric("Waist-to-hip", m["whr"], help=m["whr_cat"])
    c4.metric("Ideal weight range", f"{m['ideal_range'][0]}–{m['ideal_range'][1]} kg")

    # Healthy body-fat reference ranges
    bf_ranges = ("10–20% athletic · 14–25% fitness · 18–30% average"
                 if p.gender == "Male" else
                 "18–28% athletic · 21–33% fitness · 25–35% average")
    theme.insight(f"<b>Body-fat context ({p.gender}):</b> {bf_ranges}. "
                  f"You're at <b>{m['body_fat']}%</b> ({m['fat_source']}).")
    theme.insight(f"<b>WHR risk:</b> {m['whr_cat']} (WHO). Higher WHR tracks with "
                  "visceral fat and cardiometabolic risk — the best lever is consistent "
                  "deficit + resistance training + walking, not ab exercises.")

    theme.section("🧮", "How this plan was computed (full transparency)")
    with st.expander("Show the math"):
        st.markdown(
            f"""
**Persona assignment** — K-Means (k = 4) on *collectable* features
(Age, BMI, Body fat %, Frequency, Experience, Session length), trained on the
973-session Kaggle dataset. Your nearest centroid = **{plan['persona_name']}**.

**Calorie estimate per session** — blend of:
1. Gradient-Boosted Regressor (Age, Weight, Height, Avg HR, Duration, Frequency,
   Experience, Workout type, Gender) — holdout **R² = {plan['calorie_model']['r2']},
   MAE = {plan['calorie_model']['mae']} kcal**.
2. MET equation: `MET × weight(kg) × hours` (HIIT 9 / Cardio 8 / Strength 6 / Yoga 3).

**Honesty box:** the public dataset is near-deterministic — calories are essentially a
closed-form function of HR × duration (hence R² ≈ 0.99). Treat absolute calorie numbers
as *relative intensity guidance*, not lab measurements. Deficit/surplus outcomes depend
on adherence, sleep and genetics.

**Intensity zones** — Tanaka HRmax (208 − 0.7 × age = {plan['hr_max']} bpm).
{'Karvonen zones using resting HR ' + str(p.resting_hr) + ' bpm.' if p.resting_hr else 'Resting HR not provided — zones shown as %HRmax.'}

**Nutrition** — BMR: Mifflin-St Jeor · TDEE multiplier: 1.375–1.9 by training days ·
goal delta {'−500 (weight loss)' if p.goal == 'weight_loss' else '+250 (muscle gain)' if p.goal == 'muscle_gain' else '0 (maintenance)'} ·
protein/fat per goal with diet overrides ({p.diet}).

**Plan structure** — weekly split templates chosen by days available, goal and experience
(e.g. PPL for advanced muscle gain, Full Body for beginners). Exercises filtered by
level ≤ your experience, with your body focus weighted first.
            """)
    st.warning(
        "This plan is general fitness guidance from population averages — NOT medical "
        "advice. Consult a physician before starting, especially with cardiovascular "
        "disease, hypertension, diabetes, pregnancy or musculoskeletal issues. "
        "Nutrition targets are estimates; adjust to your response and talk to a "
        "registered dietitian for clinical needs.", icon="🩺")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    theme.apply("💪", "Gym Member — Workout & Nutrition Recommender")
    theme.hero(
        "💪", "Workout & Nutrition Recommender",
        "A personalized program built from 973 real gym sessions: K-Means persona "
        "assignment, physiology-based nutrition (BMR/TDEE/macros), HR-zone targeted "
        "sessions with estimated calorie burn, recovery protocol and a downloadable PDF.",
        ["Machine Learning", "K-Means Personas", "Mifflin-St Jeor", "Karvonen Zones",
         "Gradient Boosting", "Streamlit"],
    )

    init_state()
    import bridge
    bridge.navigation()
    bridge.receive_profile()
    if st.session_state.get("imported_profile"):
        st.info("Member profile imported. Review the prefilled values. Goals and missing measurements remain editable defaults; persona is recalculated by this app.")

    with st.sidebar:
        st.subheader("🏋️ How it works")
        st.markdown(
            "1. **Assess** — 3 quick steps (body, goals, lifestyle)\n"
            "2. **Assign** — K-Means persona trained on real gym data\n"
            "3. **Plan** — split, exercises, sets/reps, HR zones, calories\n"
            "4. **Fuel** — BMR/TDEE, macros, hydration, recovery\n"
            "5. **Track** — download the PDF, re-test in 4–6 weeks\n")
        st.divider()
        st.subheader("📊 Dataset")
        st.caption("Kaggle 'Gym Members Exercise Dataset' — 973 sessions, "
                   "no missing values. [Source](https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset)")
        st.divider()
        st.subheader("🤝 Companion project")
        st.caption("Project 1 — Gym Member Segmentation & Clustering "
                   "(the persona engine this app builds on).")
        st.divider()
        if st.session_state["plan"] is not None:
            if st.button("🔄 Start over", use_container_width=True):
                reset_all()
                st.rerun()

    with st.sidebar:
        st.subheader("⚠️ Disclaimer")
        st.caption(engine.DISCLAIMER)

    if st.session_state["step"] < 4:
        stepper()
        if st.session_state["step"] == 1:
            step_body()
        elif st.session_state["step"] == 2:
            step_profile()
        elif st.session_state["step"] == 3:
            step_lifestyle()
        return

    # ---- Results ----------------------------------------------------------
    plan = st.session_state["plan"]
    c1, c2 = st.columns([3, 1])
    with c1:
        st.success(f"Plan generated — you're a **{plan['persona_name']}**. "
                   "Everything below updates from the same engine.", icon="🎯")
    with c2:
        if st.session_state.get("pdf_bytes"):
            st.download_button(
                "⬇️ Download PDF plan",
                data=st.session_state["pdf_bytes"],
                file_name=f"workout_nutrition_plan_{plan['persona_name'].lower().replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True)
        else:
            st.warning("PDF export needs one package: run "
                       "`pip install fpdf2` "
                       f"({st.session_state.get('pdf_error', 'fpdf2 not installed')})",
                       icon="⬇️")

    tabs = st.tabs(["🎭 Your Persona", "🏋️ Weekly Workout Plan",
                    "🥗 Nutrition & Recovery", "📈 Progress & Insights"])
    with tabs[0]:
        tab_persona(plan)
    with tabs[1]:
        tab_workout(plan)
    with tabs[2]:
        tab_nutrition(plan)
    with tabs[3]:
        tab_progress(plan)

    theme.footer(project_name="Gym Member — Workout & Nutrition Recommender",
                 author_name="Fotros")


if __name__ == "__main__":
    main()
