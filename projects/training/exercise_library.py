"""Exercise library for the Workout & Nutrition Recommender.

Every exercise is tagged with:
    body_part    — primary muscle group (chest/back/shoulders/arms/legs/glutes/core/full_body/cardio/mobility)
    focus        — which Target Body Focus buckets it belongs to
    equipment    — bodyweight | dumbbell | barbell | machine | cable | kettlebell | band | cardio_machine
    level        — minimum experience required (1 = beginner, 2 = intermediate, 3 = advanced)
    goals        — goals it suits best
    pattern      — movement pattern, used to guarantee balanced sessions
                   (push | pull | squat | hinge | core | carry | cardio | mobility)
    cue          — one-line coaching cue shown in the app and PDF
"""

EXERCISES = [
    # ---------------- CHEST / PUSH ----------------
    dict(name="Push-Up", body_part="chest", focus=["upper_body", "full_body"], equipment="bodyweight", level=1, goals=["general", "weight_loss", "endurance"], pattern="push", cue="Ribs down, elbows 45°, chest to floor."),
    dict(name="Incline Dumbbell Press", body_part="chest", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="push", cue="Press up and slightly back; control the eccentric."),
    dict(name="Flat Barbell Bench Press", body_part="chest", focus=["upper_body"], equipment="barbell", level=2, goals=["muscle_gain"], pattern="push", cue="Retract scapulae, feet planted, bar to mid-chest."),
    dict(name="Dumbbell Flye", body_part="chest", focus=["upper_body"], equipment="dumbbell", level=2, goals=["muscle_gain"], pattern="push", cue="Soft elbows; stretch, don't press, to feel chest."),
    dict(name="Cable Chest Press", body_part="chest", focus=["upper_body"], equipment="cable", level=1, goals=["muscle_gain", "general"], pattern="push", cue="Constant tension; squeeze at full extension."),
    dict(name="Machine Chest Press", body_part="chest", focus=["upper_body"], equipment="machine", level=1, goals=["general", "weight_loss"], pattern="push", cue="Set seat so handles are at mid-chest; full ROM."),
    dict(name="Dips", body_part="chest", focus=["upper_body"], equipment="bodyweight", level=2, goals=["muscle_gain", "endurance"], pattern="push", cue="Lean forward, elbows tracking back; add weight when 12 reps feel easy."),

    # ---------------- BACK / PULL ----------------
    dict(name="Lat Pulldown", body_part="back", focus=["upper_body", "full_body"], equipment="cable", level=1, goals=["general", "muscle_gain", "weight_loss"], pattern="pull", cue="Pull bar to upper chest; chest tall, elbows down."),
    dict(name="Seated Cable Row", body_part="back", focus=["upper_body"], equipment="cable", level=1, goals=["muscle_gain", "general"], pattern="pull", cue="Drive elbows behind hips; squeeze shoulder blades."),
    dict(name="One-Arm Dumbbell Row", body_part="back", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="pull", cue="Flat back; pull elbow to hip, not to shoulder."),
    dict(name="Assisted Pull-Up", body_part="back", focus=["upper_body"], equipment="machine", level=1, goals=["muscle_gain", "endurance"], pattern="pull", cue="Full hang to chin over bar; no kipping."),
    dict(name="Barbell Bent-Over Row", body_part="back", focus=["upper_body"], equipment="barbell", level=2, goals=["muscle_gain"], pattern="pull", cue="Hinge ~45°, brace hard, bar to lower ribs."),
    dict(name="Deadlift", body_part="back", focus=["full_body", "lower_body"], equipment="barbell", level=2, goals=["muscle_gain", "strength" if False else "general"], pattern="hinge", cue="Push the floor away; lock out hips and knees together."),
    dict(name="Face Pull", body_part="back", focus=["upper_body", "core_abs"], equipment="cable", level=1, goals=["general", "muscle_gain"], pattern="pull", cue="Rope to forehead, elbows high — posture fixer."),
    dict(name="Kettlebell Swing", body_part="back", focus=["full_body", "glutes_legs", "lower_body"], equipment="kettlebell", level=2, goals=["weight_loss", "endurance", "general"], pattern="hinge", cue="Snap hips forward; the bell floats, arms relaxed."),

    # ---------------- SHOULDERS ----------------
    dict(name="Dumbbell Overhead Press", body_part="shoulders", focus=["upper_body", "full_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="push", cue="Belly brace, ribcage down; press to ear height."),
    dict(name="Seated Machine Shoulder Press", body_part="shoulders", focus=["upper_body"], equipment="machine", level=1, goals=["general", "muscle_gain"], pattern="push", cue="Back flat on pad; full lockout without shrugging."),
    dict(name="Lateral Raise", body_part="shoulders", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="push", cue="Lead with pinkies, elbows slightly forward."),
    dict(name="Rear Delt Fly", body_part="shoulders", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="pull", cue="Chest supported; rear delts, not traps."),
    dict(name="Arnold Press", body_part="shoulders", focus=["upper_body"], equipment="dumbbell", level=2, goals=["muscle_gain"], pattern="push", cue="Rotate from palms-in to palms-forward through the press."),
    dict(name="Barbell Overhead Press", body_part="shoulders", focus=["upper_body", "full_body"], equipment="barbell", level=3, goals=["muscle_gain"], pattern="push", cue="Squeeze glutes and abs; bar path vertical."),

    # ---------------- ARMS ----------------
    dict(name="Dumbbell Biceps Curl", body_part="arms", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain", "general"], pattern="pull", cue="Elbows pinned; control the negative 2–3s."),
    dict(name="Hammer Curl", body_part="arms", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain"], pattern="pull", cue="Neutral grip; thickens the brachialis."),
    dict(name="Triceps Cable Pushdown", body_part="arms", focus=["upper_body"], equipment="cable", level=1, goals=["muscle_gain", "general"], pattern="push", cue="Elbows fixed at sides; squeeze at lockout."),
    dict(name="Overhead Triceps Extension", body_part="arms", focus=["upper_body"], equipment="dumbbell", level=1, goals=["muscle_gain"], pattern="push", cue="Elbows narrow, long head emphasis."),
    dict(name="Close-Grip Bench Press", body_part="arms", focus=["upper_body"], equipment="barbell", level=2, goals=["muscle_gain"], pattern="push", cue="Shoulder-width grip, elbows tucked."),

    # ---------------- LEGS / QUADS ----------------
    dict(name="Back Squat", body_part="legs", focus=["lower_body", "glutes_legs", "full_body"], equipment="barbell", level=2, goals=["muscle_gain", "general"], pattern="squat", cue="Brace big; sit between the hips below parallel."),
    dict(name="Goblet Squat", body_part="legs", focus=["lower_body", "glutes_legs", "full_body"], equipment="kettlebell", level=1, goals=["general", "weight_loss", "muscle_gain"], pattern="squat", cue="Chest tall, elbows inside knees at the bottom."),
    dict(name="Leg Press", body_part="legs", focus=["lower_body", "glutes_legs"], equipment="machine", level=1, goals=["general", "muscle_gain", "weight_loss"], pattern="squat", cue="Full ROM; knees track over toes, lower back stays down."),
    dict(name="Walking Lunge", body_part="legs", focus=["lower_body", "glutes_legs", "full_body"], equipment="dumbbell", level=1, goals=["weight_loss", "endurance", "general"], pattern="squat", cue="Long stride, torso tall, knee over ankle."),
    dict(name="Bulgarian Split Squat", body_part="legs", focus=["lower_body", "glutes_legs"], equipment="dumbbell", level=2, goals=["muscle_gain", "weight_loss"], pattern="squat", cue="Rear foot elevated; front heel drives the floor."),
    dict(name="Front Squat", body_part="legs", focus=["lower_body", "full_body"], equipment="barbell", level=3, goals=["muscle_gain"], pattern="squat", cue="Elbows high; vertical torso, quad dominant."),
    dict(name="Leg Extension", body_part="legs", focus=["lower_body"], equipment="machine", level=1, goals=["muscle_gain", "general"], pattern="squat", cue="Pause at the top; controlled negative."),
    dict(name="Hack Squat", body_part="legs", focus=["lower_body", "glutes_legs"], equipment="machine", level=2, goals=["muscle_gain"], pattern="squat", cue="Feet mid-platform; don't let hips shoot up first."),

    # ---------------- GLUTES / HAMSTRINGS / HINGE ----------------
    dict(name="Romanian Deadlift", body_part="glutes", focus=["lower_body", "glutes_legs", "full_body"], equipment="barbell", level=2, goals=["muscle_gain", "general"], pattern="hinge", cue="Hips back, soft knees; feel the hamstring stretch."),
    dict(name="Hip Thrust", body_part="glutes", focus=["lower_body", "glutes_legs"], equipment="barbell", level=1, goals=["muscle_gain", "general", "weight_loss"], pattern="hinge", cue="Ribs down, chin tucked; squeeze 2s at lockout."),
    dict(name="Glute Bridge", body_part="glutes", focus=["lower_body", "glutes_legs", "core_abs"], equipment="bodyweight", level=1, goals=["general", "flexibility", "weight_loss"], pattern="hinge", cue="Posterior pelvic tilt at the top."),
    dict(name="Lying Leg Curl", body_part="glutes", focus=["lower_body", "glutes_legs"], equipment="machine", level=1, goals=["muscle_gain", "general"], pattern="hinge", cue="Hips glued to pad; full stretch each rep."),
    dict(name="Cable Kickback", body_part="glutes", focus=["glutes_legs", "lower_body"], equipment="cable", level=1, goals=["muscle_gain", "weight_loss"], pattern="hinge", cue="Small ROM, big squeeze; no lower-back arch."),
    dict(name="Single-Leg Romanian Deadlift", body_part="glutes", focus=["lower_body", "glutes_legs"], equipment="dumbbell", level=2, goals=["muscle_gain", "endurance"], pattern="hinge", cue="Square hips; reach for the floor, not depth."),

    # ---------------- CORE ----------------
    dict(name="Plank", body_part="core", focus=["core_abs", "full_body"], equipment="bodyweight", level=1, goals=["general", "weight_loss", "endurance", "flexibility"], pattern="core", cue="Posterior pelvic tilt; squeeze glutes and quads."),
    dict(name="Dead Bug", body_part="core", focus=["core_abs", "full_body"], equipment="bodyweight", level=1, goals=["general", "flexibility"], pattern="core", cue="Lower back pressed into the floor; move opposite limbs."),
    dict(name="Hanging Knee Raise", body_part="core", focus=["core_abs"], equipment="bodyweight", level=2, goals=["muscle_gain", "weight_loss"], pattern="core", cue="Posterior tilt — bring pelvis to ribs, not knees to chest."),
    dict(name="Cable Woodchop", body_part="core", focus=["core_abs"], equipment="cable", level=2, goals=["weight_loss", "general", "endurance"], pattern="core", cue="Rotate through the ribcage, hips stable."),
    dict(name="Ab Wheel Rollout", body_part="core", focus=["core_abs"], equipment="bodyweight", level=3, goals=["muscle_gain", "general"], pattern="core", cue="Glutes tight; only roll as far as you can resist extension."),
    dict(name="Russian Twist", body_part="core", focus=["core_abs"], equipment="bodyweight", level=1, goals=["weight_loss", "general"], pattern="core", cue="Feet elevated if advanced; rotate ribs, not just arms."),
    dict(name="Side Plank", body_part="core", focus=["core_abs"], equipment="bodyweight", level=1, goals=["general", "flexibility"], pattern="core", cue="Stack shoulders/hips; lift hips high."),

    # ---------------- FULL BODY / METABOLIC ----------------
    dict(name="Burpee", body_part="full_body", focus=["full_body"], equipment="bodyweight", level=1, goals=["weight_loss", "endurance"], pattern="cardio", cue="Chest to floor, jump tall; breathe steadily."),
    dict(name="Thruster", body_part="full_body", focus=["full_body"], equipment="dumbbell", level=2, goals=["weight_loss", "endurance"], pattern="squat", cue="Squat then drive overhead in one motion."),
    dict(name="Clean & Press", body_part="full_body", focus=["full_body"], equipment="barbell", level=3, goals=["weight_loss", "endurance", "muscle_gain"], pattern="hinge", cue="Pull the bar vertical; catch and press."),
    dict(name="Kettlebell Snatch", body_part="full_body", focus=["full_body"], equipment="kettlebell", level=3, goals=["endurance", "weight_loss"], pattern="hinge", cue="Keep the bell close; punch through at the top."),
    dict(name="Man-Maker", body_part="full_body", focus=["full_body"], equipment="dumbbell", level=3, goals=["weight_loss", "endurance"], pattern="push", cue="Push-up, row each arm, clean, press, repeat."),

    # ---------------- CARDIO ----------------
    dict(name="Treadmill Incline Walk", body_part="cardio", focus=["full_body", "glutes_legs"], equipment="cardio_machine", level=1, goals=["weight_loss", "general", "flexibility"], pattern="cardio", cue="8–12% incline, brisk pace, hands off rails."),
    dict(name="Zone-2 Cycling", body_part="cardio", focus=["full_body", "lower_body"], equipment="cardio_machine", level=1, goals=["weight_loss", "endurance", "general"], pattern="cardio", cue="Conversational pace; 60–70% max HR."),
    dict(name="Rowing Intervals", body_part="cardio", focus=["full_body"], equipment="cardio_machine", level=2, goals=["endurance", "weight_loss"], pattern="cardio", cue="Drive legs → hips → arms; recover in reverse."),
    dict(name="Sled Push", body_part="cardio", focus=["full_body", "lower_body", "glutes_legs"], equipment="machine", level=2, goals=["weight_loss", "endurance"], pattern="cardio", cue="Low hips, long strides; 20–30m efforts."),
    dict(name="Battle Ropes", body_part="cardio", focus=["full_body", "upper_body"], equipment="bodyweight", level=1, goals=["weight_loss", "endurance"], pattern="cardio", cue="Hinge slightly; alternate waves, breathe out on effort."),
    dict(name="Jump Rope", body_part="cardio", focus=["full_body", "glutes_legs"], equipment="bodyweight", level=1, goals=["endurance", "weight_loss"], pattern="cardio", cue="Stay on the balls of feet; small jumps."),
    dict(name="Assault Bike Sprints", body_part="cardio", focus=["full_body"], equipment="cardio_machine", level=2, goals=["weight_loss", "endurance"], pattern="cardio", cue="Max effort 15–30s, full recovery between."),

    # ---------------- MOBILITY / FLEXIBILITY ----------------
    dict(name="World's Greatest Stretch", body_part="mobility", focus=["core_abs", "full_body"], equipment="bodyweight", level=1, goals=["flexibility", "general"], pattern="mobility", cue="Lunge, elbow to instep, rotate up — 5/side."),
    dict(name="90/90 Hip Flow", body_part="mobility", focus=["glutes_legs", "lower_body"], equipment="bodyweight", level=1, goals=["flexibility"], pattern="mobility", cue="Switch knees side to side without hands."),
    dict(name="Cat-Cow", body_part="mobility", focus=["core_abs", "full_body"], equipment="bodyweight", level=1, goals=["flexibility", "general"], pattern="mobility", cue="Segment the spine one vertebra at a time."),
    dict(name="Downward Dog to Cobra Flow", body_part="mobility", focus=["full_body"], equipment="bodyweight", level=1, goals=["flexibility", "general"], pattern="mobility", cue="Move with breath; exhale into each shape."),
    dict(name="Thoracic Rotation (Quadruped)", body_part="mobility", focus=["core_abs", "upper_body"], equipment="bodyweight", level=1, goals=["flexibility", "general"], pattern="mobility", cue="Elbow traces a big arc; hips stay square."),
    dict(name="Pigeon Pose", body_part="mobility", focus=["glutes_legs", "lower_body"], equipment="bodyweight", level=1, goals=["flexibility"], pattern="mobility", cue="Breathe into the hip; 60–90s per side."),
    dict(name="Sun Salutation Flow", body_part="mobility", focus=["full_body"], equipment="bodyweight", level=1, goals=["flexibility", "general", "weight_loss"], pattern="mobility", cue="One breath per movement; 5 rounds."),
]

WARMUP = [
    "5 min easy cardio (bike, brisk walk or rope) to raise core temp",
    "Dynamic mobility: arm circles, hip openers, leg swings — 60–90s each",
    "1–2 ramp-up sets per compound lift (50% → 70% → 85% of working weight)",
    "Activation: band pull-aparts, glute bridges, dead bugs — 2 × 10",
]

COOLDOWN = [
    "3–5 min slow walk + nasal breathing to bring HR below 120 bpm",
    "Static stretching 30–60s per muscle worked (hips, hamstrings, chest, lats)",
    "Hydrate: 500 ml water within 30 min post-session",
    "Note session RPE (1–10) in a log — feed it back into next week's plan",
]

MEAL_IDEAS = {
    "Omnivore": ["Greek yogurt + oats + berries", "Chicken breast + rice + veggies", "Egg whites + whole-grain toast", "Salmon + quinoa + salad", "Cottage cheese + fruit"],
    "Vegetarian": ["Paneer/tofu stir-fry + rice", "Lentil dal + roti + curd", "Oats + milk + nuts", "Chickpea salad bowls", "Egg & cheese quesadilla"],
    "Vegan": ["Tofu scramble + toast", "Lentil/bean curry + rice", "Overnight oats + soy milk + seeds", "Chickpea & tahini bowl", "Tempeh Buddha bowl"],
    "Keto": ["Eggs + avocado + bacon", "Bunless burger + side salad", "Salmon + buttered broccoli", "Greek yogurt + walnuts", "Zucchini noodles + pesto + chicken"],
    "High-Protein": ["4-egg omelet + toast", "Protein shake + banana + oats", "Chicken/tuna/tofu at every meal", "Skyr + granola", "Cottage cheese before bed"],
}

# MET values (Compendium of Physical Activities) for the calorie estimate
MET_BY_WORKOUT = {
    "HIIT": 9.0,
    "Strength": 6.0,
    "Cardio": 8.0,
    "Yoga": 3.0,
}

ACTIVITY_MULTIPLIER = {1: 1.375, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.55, 6: 1.725, 7: 1.9}

GOAL_LABELS = {
    "weight_loss": "Weight Loss",
    "muscle_gain": "Muscle Gain",
    "endurance": "Endurance",
    "general": "General Fitness",
    "flexibility": "Flexibility",
}

FOCUS_LABELS = {
    "full_body": "Full Body",
    "upper_body": "Upper Body",
    "lower_body": "Lower Body",
    "core_abs": "Core / Abs",
    "glutes_legs": "Glutes & Legs",
}
