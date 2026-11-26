"""
StreamScope Synthetic OTT Data Generator
=========================================
Generates realistic, logically coherent synthetic datasets for OTT analytics:
- 10,000 Users
- 4 Subscription Plans
- 80 Content items (Movies and Web Series)
- ~8,200 Subscription records (New, Renewals, Cancellations, Reactivations)
- ~105,000 Viewing Sessions
- ~220,000 App Interaction Events

All logic uses fixed random seeds for deterministic reproducibility.
Output: CSV files in data/raw/ and representative sample in data/sample_data/
"""

import os
import csv
import random
from datetime import datetime, date, timedelta

# Configuration & Seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)
FOLLOWUP_DATE = date(2026, 1, 31)  # 30-day follow-up for churn measurement

NUM_USERS = 10000
NUM_CONTENT = 80
TARGET_SESSIONS = 105000

OUTPUT_RAW_DIR = os.path.join("data", "raw")
OUTPUT_SAMPLE_DIR = os.path.join("data", "sample_data")
OUTPUT_PROCESSED_DIR = os.path.join("data", "processed")

os.makedirs(OUTPUT_RAW_DIR, exist_ok=True)
os.makedirs(OUTPUT_SAMPLE_DIR, exist_ok=True)
os.makedirs(OUTPUT_PROCESSED_DIR, exist_ok=True)

print("=" * 60)
print("StreamScope OTT Analytics - Synthetic Data Generator")
print(f"Random Seed: {RANDOM_SEED}")
print(f"Observation Period: {START_DATE} to {END_DATE} (Follow-up: {FOLLOWUP_DATE})")
print("=" * 60)

# -------------------------------------------------------------
# 1. GENERATE PLANS
# -------------------------------------------------------------
plans_data = [
    {"plan_id": 1, "plan_name": "Basic with Ads", "monthly_price": 6.99, "max_screens": 1, "video_quality": "HD 720p"},
    {"plan_id": 2, "plan_name": "Standard HD", "monthly_price": 11.99, "max_screens": 2, "video_quality": "Full HD 1080p"},
    {"plan_id": 3, "plan_name": "Premium 4K", "monthly_price": 16.99, "max_screens": 4, "video_quality": "4K Ultra HD"},
    {"plan_id": 4, "plan_name": "Family Ultra", "monthly_price": 21.99, "max_screens": 4, "video_quality": "4K HDR + Atmos"}
]

print(f"-> Generated {len(plans_data)} subscription plans.")

# -------------------------------------------------------------
# 2. GENERATE CONTENT (80 Movies and Web Series)
# -------------------------------------------------------------
content_titles = [
    # Sci-Fi & Fantasy
    ("Cyber City 2099", "Sci-Fi & Fantasy", "Web Series", 55),
    ("Neon Horizon", "Sci-Fi & Fantasy", "Movie", 124),
    ("The Quantum Paradox", "Sci-Fi & Fantasy", "Movie", 138),
    ("Chronicles of Aethelgard", "Sci-Fi & Fantasy", "Web Series", 60),
    ("Starlight Colony", "Sci-Fi & Fantasy", "Web Series", 50),
    ("Solaris Drift", "Sci-Fi & Fantasy", "Movie", 112),
    ("Temporal Echoes", "Sci-Fi & Fantasy", "Movie", 105),
    ("The AI Prophecy", "Sci-Fi & Fantasy", "Web Series", 48),
    ("Deep Orbit", "Sci-Fi & Fantasy", "Movie", 128),
    ("Vortex", "Sci-Fi & Fantasy", "Web Series", 52),

    # Action & Adventure
    ("Apex Protocol", "Action & Adventure", "Movie", 118),
    ("Redline Velocity", "Action & Adventure", "Movie", 126),
    ("Shadow Syndicate", "Action & Adventure", "Web Series", 54),
    ("The Extraction Unit", "Action & Adventure", "Movie", 110),
    ("Strike Force: Omega", "Action & Adventure", "Movie", 132),
    ("Vanguard Reborn", "Action & Adventure", "Web Series", 58),
    ("Rogue Agent", "Action & Adventure", "Movie", 115),
    ("Mountain Siege", "Action & Adventure", "Movie", 108),
    ("Ironclad Horizon", "Action & Adventure", "Movie", 140),
    ("Zero Hour Escape", "Action & Adventure", "Web Series", 45),

    # Drama
    ("The Boardroom", "Drama", "Web Series", 58),
    ("Echoes of Silence", "Drama", "Movie", 135),
    ("Autumn in Paris", "Drama", "Movie", 110),
    ("Dynasty of Steel", "Drama", "Web Series", 62),
    ("The Last Conductor", "Drama", "Movie", 122),
    ("Behind the Gavel", "Drama", "Web Series", 50),
    ("Shattered Glass", "Drama", "Movie", 104),
    ("The Family Ledger", "Drama", "Web Series", 56),
    ("Letters to Nowhere", "Drama", "Movie", 116),
    ("A Quiet Storm", "Drama", "Movie", 98),

    # Comedy
    ("Office Pandemonium", "Comedy", "Web Series", 30),
    ("Roommates & Ruin", "Comedy", "Web Series", 28),
    ("The Accidental Billionaire", "Comedy", "Movie", 96),
    ("Sunday Roast", "Comedy", "Movie", 102),
    ("Startup Mayhem", "Comedy", "Web Series", 32),
    ("Grandpa Goes Viral", "Comedy", "Movie", 90),
    ("Wedding Crashes Again", "Comedy", "Movie", 94),
    ("Couch Detectives", "Comedy", "Web Series", 35),
    ("Double Date Disaster", "Comedy", "Movie", 88),
    ("Suburban Shenanigans", "Comedy", "Web Series", 26),

    # Thriller & Mystery
    ("The Vanishing Room", "Thriller & Mystery", "Movie", 114),
    ("Midnight Caller", "Thriller & Mystery", "Web Series", 46),
    ("Cold Harbor Secrets", "Thriller & Mystery", "Web Series", 52),
    ("Blind Alley", "Thriller & Mystery", "Movie", 108),
    ("Whispers in the Dark", "Thriller & Mystery", "Movie", 120),
    ("The Cipher Key", "Thriller & Mystery", "Web Series", 49),
    ("Blackmail Boulevard", "Thriller & Mystery", "Movie", 102),
    ("The Silent Witness", "Thriller & Mystery", "Movie", 118),
    ("Fog on the Thames", "Thriller & Mystery", "Web Series", 55),
    ("Deception Bay", "Thriller & Mystery", "Movie", 110),

    # Documentary
    ("Planet Wild: Oceans", "Documentary", "Web Series", 50),
    ("Silicon Pioneers", "Documentary", "Movie", 95),
    ("Formula Velocity", "Documentary", "Web Series", 45),
    ("The Deep Cosmos", "Documentary", "Movie", 105),
    ("Culinary Masters", "Documentary", "Web Series", 42),
    ("Rise of the Champions", "Documentary", "Movie", 112),
    ("Ancient Wonders Unveiled", "Documentary", "Web Series", 55),
    ("The Code Breakers", "Documentary", "Movie", 88),
    ("Art of the Heist", "Documentary", "Web Series", 48),
    ("Guardians of the Forest", "Documentary", "Movie", 92),

    # Animation
    ("Cyber Samurai", "Animation", "Web Series", 24),
    ("The Cloud Kingdom", "Animation", "Movie", 92),
    ("Pixel Pals", "Animation", "Web Series", 22),
    ("The Iron Dragon", "Animation", "Movie", 104),
    ("Cosmic Critters", "Animation", "Web Series", 25),
    ("Starfall Quest", "Animation", "Movie", 86),
    ("Mech Warriors Academy", "Animation", "Web Series", 28),
    ("Tales of the Spirit Forest", "Animation", "Movie", 98),
    ("Dreamscape Explorers", "Animation", "Web Series", 24),
    ("The Golden Feather", "Animation", "Movie", 84),

    # Romance
    ("Summer in Florence", "Romance", "Movie", 106),
    ("Coffee & Serendipity", "Romance", "Movie", 94),
    ("Heartstrings", "Romance", "Web Series", 44),
    ("The Art of Falling", "Romance", "Movie", 100),
    ("Under Manhattan Lights", "Romance", "Movie", 112),
    ("Written in the Stars", "Romance", "Web Series", 40),
    ("Second Chance Cafe", "Romance", "Movie", 98),
    ("Winter Waltz", "Romance", "Movie", 104),
    ("A Sunset Promise", "Romance", "Movie", 92),
    ("Destined for You", "Romance", "Web Series", 48),
]

content_data = []
for idx, (title, genre, ctype, duration) in enumerate(content_titles, start=1):
    release_year = random.choice([2019, 2020, 2021, 2022, 2023, 2024, 2025])
    content_data.append({
        "content_id": idx,
        "title": title,
        "genre": genre,
        "release_year": release_year,
        "content_type": ctype,
        "duration_minutes": duration
    })

print(f"-> Generated {len(content_data)} content titles across 8 genres.")

# -------------------------------------------------------------
# 3. GENERATE USERS & ENGAGEMENT PERSONAS
# -------------------------------------------------------------
countries = ["United States", "United Kingdom", "Canada", "India", "Germany", "Australia"]
country_weights = [0.38, 0.18, 0.12, 0.16, 0.09, 0.07]

age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
age_weights = [0.22, 0.38, 0.22, 0.12, 0.06]

acquisition_channels = ["Organic Search", "Social Media", "Paid Search", "Referral", "Email Campaign", "Affiliate"]
channel_weights = [0.28, 0.25, 0.18, 0.12, 0.10, 0.07]

devices = ["Smart TV", "Mobile", "Laptop", "Tablet"]
device_weights = [0.42, 0.32, 0.18, 0.08]

# Persona distribution:
# Persona 1: Power Streamer (Highly Engaged) ~22%
# Persona 2: Casual Regular (Moderately Engaged) ~36%
# Persona 3: Low Engagement / Weekend Only ~24%
# Persona 4: Dormant / Trial Dropoff ~18%

total_days_2025 = (END_DATE - START_DATE).days + 1

users_data = []
user_personas = {}  # user_id -> persona dict

for uid in range(1, NUM_USERS + 1):
    # Signup date distributed across 2025 with slight seasonality (peak Jan, summer, autumn)
    signup_day_offset = int(random.triangular(0, total_days_2025 - 1, total_days_2025 * 0.4))
    signup_date = START_DATE + timedelta(days=signup_day_offset)
    
    country = random.choices(countries, weights=country_weights)[0]
    age_group = random.choices(age_groups, weights=age_weights)[0]
    channel = random.choices(acquisition_channels, weights=channel_weights)[0]
    preferred_device = random.choices(devices, weights=device_weights)[0]
    
    # Assign persona based on channel affinity and random weight
    # Referral and Organic tend to have higher engagement
    persona_rnd = random.random()
    if channel in ["Referral", "Organic Search"]:
        if persona_rnd < 0.30:
            persona = "Power Streamer"
        elif persona_rnd < 0.70:
            persona = "Casual Regular"
        elif persona_rnd < 0.88:
            persona = "Low Engagement"
        else:
            persona = "Dormant"
    elif channel in ["Social Media", "Paid Search"]:
        if persona_rnd < 0.16:
            persona = "Power Streamer"
        elif persona_rnd < 0.48:
            persona = "Casual Regular"
        elif persona_rnd < 0.76:
            persona = "Low Engagement"
        else:
            persona = "Dormant"
    else:
        if persona_rnd < 0.20:
            persona = "Power Streamer"
        elif persona_rnd < 0.55:
            persona = "Casual Regular"
        elif persona_rnd < 0.80:
            persona = "Low Engagement"
        else:
            persona = "Dormant"

    user_personas[uid] = persona

    users_data.append({
        "user_id": uid,
        "signup_date": signup_date.isoformat(),
        "country": country,
        "age_group": age_group,
        "acquisition_channel": channel,
        "preferred_device": preferred_device
    })

print(f"-> Generated {len(users_data)} users with realistic demographic distribution.")

# -------------------------------------------------------------
# 4. GENERATE SUBSCRIPTIONS (Lifecycle: New, Renew, Cancel, Reactivate)
# -------------------------------------------------------------
# Some registered users never convert to a paid subscription (~18%, mostly dormant)
# Paid users subscribe on or slightly after signup_date
# Subscriptions can be active, canceled, or renewed

subscriptions_data = []
sub_id_counter = 1

user_sub_history = {}  # user_id -> list of active periods [(start, end)]

cancellation_reasons = [
    "Price too high",
    "Lack of content",
    "Technical issues",
    "Switched to competitor",
    "Infrequent usage",
    "Found alternative"
]
reason_weights = [0.32, 0.24, 0.09, 0.15, 0.14, 0.06]

plan_choices = [1, 2, 3, 4]
plan_weights = [0.25, 0.45, 0.22, 0.08]

plan_pricing = {1: 6.99, 2: 11.99, 3: 16.99, 4: 21.99}

for user in users_data:
    uid = user["user_id"]
    u_signup = datetime.strptime(user["signup_date"], "%Y-%m-%d").date()
    persona = user_personas[uid]
    
    # Conversion probability by persona
    if persona == "Dormant":
        convert_prob = 0.25  # many never subscribe
    elif persona == "Low Engagement":
        convert_prob = 0.75
    else:
        convert_prob = 0.94  # power / casual almost always subscribe

    if random.random() > convert_prob:
        continue  # Registered but never subscribed

    # First subscription starts 0 to 5 days after signup
    first_sub_start = u_signup + timedelta(days=random.randint(0, 5))
    if first_sub_start > FOLLOWUP_DATE:
        continue

    chosen_plan = random.choices(plan_choices, weights=plan_weights)[0]
    cycle = random.choices(["Monthly", "Annual"], weights=[0.85, 0.15])[0]
    monthly_fee = plan_pricing[chosen_plan]
    if cycle == "Annual":
        monthly_fee = round(monthly_fee * 0.82, 2)  # 18% annual discount

    # Subscription tenure depends on persona and plan
    # Power streamers stay longer; low engagement / dormant churn early
    if persona == "Power Streamer":
        churn_prob = 0.12
        avg_months = random.randint(5, 12)
    elif persona == "Casual Regular":
        churn_prob = 0.28
        avg_months = random.randint(3, 9)
    elif persona == "Low Engagement":
        churn_prob = 0.58
        avg_months = random.randint(1, 4)
    else: # Dormant
        churn_prob = 0.85
        avg_months = random.randint(1, 2)

    # First subscription duration
    cur_start = first_sub_start
    if random.random() < churn_prob:
        # User canceled
        days_active = avg_months * 30 + random.randint(-10, 15)
        cur_end = cur_start + timedelta(days=max(28, days_active))
        if cur_end > FOLLOWUP_DATE:
            cur_end = None
            status = "Active"
            reason = None
        else:
            status = "Canceled"
            reason = random.choices(cancellation_reasons, weights=reason_weights)[0]
    else:
        cur_end = None
        status = "Active"
        reason = None

    sub_record = {
        "subscription_id": sub_id_counter,
        "user_id": uid,
        "plan_id": chosen_plan,
        "start_date": cur_start.isoformat(),
        "end_date": cur_end.isoformat() if cur_end else "",
        "status": status,
        "billing_cycle": cycle,
        "monthly_fee": monthly_fee,
        "cancellation_reason": reason if reason else ""
    }
    subscriptions_data.append(sub_record)
    sub_id_counter += 1

    # Check for reactivation if the user canceled before December 2025
    if status == "Canceled" and cur_end and cur_end < date(2025, 11, 15):
        # Probability of reactivation
        reactivate_prob = 0.18 if persona in ["Power Streamer", "Casual Regular"] else 0.06
        if random.random() < reactivate_prob:
            gap_days = random.randint(35, 90)  # > 30 days gap for true reactivation
            react_start = cur_end + timedelta(days=gap_days)
            if react_start <= FOLLOWUP_DATE:
                # 2nd subscription
                react_plan = random.choices(plan_choices, weights=plan_weights)[0]
                react_sub_record = {
                    "subscription_id": sub_id_counter,
                    "user_id": uid,
                    "plan_id": react_plan,
                    "start_date": react_start.isoformat(),
                    "end_date": "",  # stays active into 2026
                    "status": "Active",
                    "billing_cycle": "Monthly",
                    "monthly_fee": plan_pricing[react_plan],
                    "cancellation_reason": ""
                }
                subscriptions_data.append(react_sub_record)
                sub_id_counter += 1

print(f"-> Generated {len(subscriptions_data)} subscription records.")

# Map user active date intervals for session generation
user_active_spans = {}
for sub in subscriptions_data:
    uid = sub["user_id"]
    s_date = datetime.strptime(sub["start_date"], "%Y-%m-%d").date()
    e_date = datetime.strptime(sub["end_date"], "%Y-%m-%d").date() if sub["end_date"] else FOLLOWUP_DATE
    if uid not in user_active_spans:
        user_active_spans[uid] = []
    user_active_spans[uid].append((s_date, e_date))

# -------------------------------------------------------------
# 5. GENERATE VIEWING SESSIONS
# -------------------------------------------------------------
# Target: ~105,000 viewing sessions
# Sessions align with user registration, subscription windows, and persona behaviors.
# Power Streamer: 25-45 sessions
# Casual Regular: 12-22 sessions
# Low Engagement: 3-8 sessions
# Dormant: 0-2 sessions

viewing_sessions = []
session_id_counter = 1

# Popularity weights for content (a few blockbusters get higher share)
content_weights = []
for c in content_data:
    cid = c["content_id"]
    # Give high weight to top 10 titles
    if cid in [1, 2, 11, 21, 31, 41, 51, 61, 71, 12]:
        content_weights.append(3.5)
    elif cid <= 30:
        content_weights.append(1.8)
    else:
        content_weights.append(1.0)

for uid in range(1, NUM_USERS + 1):
    persona = user_personas[uid]
    spans = user_active_spans.get(uid, [])
    u_signup = datetime.strptime(users_data[uid - 1]["signup_date"], "%Y-%m-%d").date()
    pref_device = users_data[uid - 1]["preferred_device"]

    if persona == "Power Streamer":
        n_sessions = random.randint(22, 38)
    elif persona == "Casual Regular":
        n_sessions = random.randint(10, 20)
    elif persona == "Low Engagement":
        n_sessions = random.randint(2, 7)
    else: # Dormant
        n_sessions = random.choices([0, 1, 2], weights=[0.45, 0.40, 0.15])[0]

    if n_sessions == 0 or not spans:
        # Free registered trial session occasionally before churn
        if persona == "Dormant" and random.random() < 0.20:
            spans = [(u_signup, u_signup + timedelta(days=7))]
            n_sessions = 1
        else:
            continue

    for _ in range(n_sessions):
        # Pick an active span
        span = random.choice(spans)
        span_days = max(1, (span[1] - span[0]).days)
        offset = random.randint(0, span_days - 1)
        sess_date = span[0] + timedelta(days=offset)
        if sess_date > FOLLOWUP_DATE:
            continue

        # Time of day (peak evenings 18:00 - 23:00)
        hour_weights = [1]*6 + [2]*6 + [4]*6 + [8]*6  # night/morning/afternoon/evening
        sess_hour = random.choices(range(24), weights=hour_weights)[0]
        sess_min = random.randint(0, 59)
        sess_sec = random.randint(0, 59)
        started_at = datetime(sess_date.year, sess_date.month, sess_date.day, sess_hour, sess_min, sess_sec)

        # Content selection
        chosen_content = random.choices(content_data, weights=content_weights)[0]
        duration = chosen_content["duration_minutes"]

        # Watch duration based on persona and content length
        if persona == "Power Streamer":
            completion_pct = min(100.0, round(random.triangular(65.0, 100.0, 92.0), 2))
        elif persona == "Casual Regular":
            completion_pct = min(100.0, round(random.triangular(40.0, 98.0, 75.0), 2))
        elif persona == "Low Engagement":
            completion_pct = min(100.0, round(random.triangular(10.0, 75.0, 35.0), 2))
        else:
            completion_pct = min(100.0, round(random.triangular(5.0, 50.0, 18.0), 2))

        watch_minutes = max(1, int(duration * (completion_pct / 100.0)))

        # Device used (80% preferred device, 20% another device)
        if random.random() < 0.80:
            dev = pref_device
        else:
            dev = random.choice(devices)

        viewing_sessions.append({
            "session_id": session_id_counter,
            "user_id": uid,
            "content_id": chosen_content["content_id"],
            "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "watch_minutes": watch_minutes,
            "completion_percentage": completion_pct,
            "device_type": dev
        })
        session_id_counter += 1

# Sort viewing sessions chronologically
viewing_sessions.sort(key=lambda s: s["started_at"])
# Re-index session_id
for idx, s in enumerate(viewing_sessions, start=1):
    s["session_id"] = idx

print(f"-> Generated {len(viewing_sessions)} viewing sessions.")

# -------------------------------------------------------------
# 6. GENERATE APP INTERACTION EVENTS
# -------------------------------------------------------------
# Event types:
# - app_open
# - search
# - content_view
# - play
# - add_to_watchlist
# - subscription_start
# - cancellation
# Target: ~200,000 - 240,000 realistic events

app_events = []
event_id_counter = 1

# A. Subscription Lifecycle Events from subscriptions_data
for sub in subscriptions_data:
    uid = sub["user_id"]
    u_dev = users_data[uid - 1]["preferred_device"]
    s_time = datetime.strptime(sub["start_date"], "%Y-%m-%d") + timedelta(hours=random.randint(9, 21), minutes=random.randint(0, 59))
    app_events.append({
        "event_id": event_id_counter,
        "user_id": uid,
        "event_timestamp": s_time.strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": "subscription_start",
        "content_id": "",
        "device_type": u_dev
    })
    event_id_counter += 1

    if sub["status"] == "Canceled" and sub["end_date"]:
        e_time = datetime.strptime(sub["end_date"], "%Y-%m-%d") + timedelta(hours=random.randint(9, 21), minutes=random.randint(0, 59))
        app_events.append({
            "event_id": event_id_counter,
            "user_id": uid,
            "event_timestamp": e_time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": "cancellation",
            "content_id": "",
            "device_type": u_dev
        })
        event_id_counter += 1

# B. Viewing-Linked Events (app_open -> [search] -> content_view -> play -> [add_to_watchlist])
# Sample a realistic portion of viewing sessions to generate preceding navigation events
# so total events reach ~220,000 without bloating file sizes
for sess in viewing_sessions:
    uid = sess["user_id"]
    cid = sess["content_id"]
    dev = sess["device_type"]
    s_dt = datetime.strptime(sess["started_at"], "%Y-%m-%d %H:%M:%S")

    # 1. App open (1 to 5 mins before playback)
    t_open = s_dt - timedelta(minutes=random.randint(2, 6))
    app_events.append({
        "event_id": event_id_counter,
        "user_id": uid,
        "event_timestamp": t_open.strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": "app_open",
        "content_id": "",
        "device_type": dev
    })
    event_id_counter += 1

    # 2. Search (optional, ~35% of sessions)
    if random.random() < 0.35:
        t_search = s_dt - timedelta(minutes=random.randint(1, 2))
        app_events.append({
            "event_id": event_id_counter,
            "user_id": uid,
            "event_timestamp": t_search.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": "search",
            "content_id": cid,
            "device_type": dev
        })
        event_id_counter += 1

    # 3. Content View (details page, ~80% of sessions)
    if random.random() < 0.80:
        t_view = s_dt - timedelta(seconds=random.randint(20, 50))
        app_events.append({
            "event_id": event_id_counter,
            "user_id": uid,
            "event_timestamp": t_view.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": "content_view",
            "content_id": cid,
            "device_type": dev
        })
        event_id_counter += 1

    # 4. Play event
    app_events.append({
        "event_id": event_id_counter,
        "user_id": uid,
        "event_timestamp": sess["started_at"],
        "event_type": "play",
        "content_id": cid,
        "device_type": dev
    })
    event_id_counter += 1

    # 5. Add to Watchlist (~12% chance)
    if random.random() < 0.12:
        t_watch = s_dt + timedelta(minutes=random.randint(5, 25))
        app_events.append({
            "event_id": event_id_counter,
            "user_id": uid,
            "event_timestamp": t_watch.strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": "add_to_watchlist",
            "content_id": cid,
            "device_type": dev
        })
        event_id_counter += 1

# Sort app events chronologically
app_events.sort(key=lambda e: e["event_timestamp"])
for idx, e in enumerate(app_events, start=1):
    e["event_id"] = idx

print(f"-> Generated {len(app_events)} app interaction events.")

# -------------------------------------------------------------
# 7. SAVE CSV FILES & SAMPLES
# -------------------------------------------------------------
datasets = {
    "users.csv": (users_data, ["user_id", "signup_date", "country", "age_group", "acquisition_channel", "preferred_device"]),
    "plans.csv": (plans_data, ["plan_id", "plan_name", "monthly_price", "max_screens", "video_quality"]),
    "content.csv": (content_data, ["content_id", "title", "genre", "release_year", "content_type", "duration_minutes"]),
    "subscriptions.csv": (subscriptions_data, ["subscription_id", "user_id", "plan_id", "start_date", "end_date", "status", "billing_cycle", "monthly_fee", "cancellation_reason"]),
    "viewing_sessions.csv": (viewing_sessions, ["session_id", "user_id", "content_id", "started_at", "watch_minutes", "completion_percentage", "device_type"]),
    "app_events.csv": (app_events, ["event_id", "user_id", "event_timestamp", "event_type", "content_id", "device_type"])
}

print("\nSaving CSV files...")
for fname, (rows, fieldnames) in datasets.items():
    raw_path = os.path.join(OUTPUT_RAW_DIR, fname)
    with open(raw_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"   [RAW] Wrote {len(rows):>7} records to {raw_path}")

    # Write representative sample (first 100 rows)
    sample_path = os.path.join(OUTPUT_SAMPLE_DIR, fname)
    with open(sample_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows[:100])
    print(f"   [SAMPLE] Wrote 100 records to {sample_path}")

print("\nSynthetic data generation completed successfully!")
