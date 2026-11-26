# Module 02: Python and Synthetic Data Generation Deep Dive

> **File Reference:** `docs/study_materials/02_PYTHON_AND_DATA_GENERATION.md`  
> **Source Script:** `scripts/generate_data.py` & `scripts/validate_data.py`  
> **Audience:** Data Analysts, Analytics Engineers, Python Developers

---

## 1. Python's Role in the StreamScope Architecture

In modern analytics engineering, Python serves as the **data simulation and quality assurance orchestration layer**. While enterprise production teams extract data from production event logs (e.g., Kafka, Segment, Snowplow) and transactional databases (e.g., PostgreSQL, Aurora), data analysts building proof-of-concept projects must generate synthetic data that faithfully mirrors real-world statistical properties.

In StreamScope, Python does **not** generate arbitrary nonsense; it executes an **agent-based behavioral simulation** where:
1. Users belong to defined behavioral personas.
2. Viewing activity is chronologically bounded by subscription start and cancellation dates.
3. Churn is preceded by an empirical drop in streaming frequency (the "engagement cliff").
4. Referential integrity is strictly maintained across 6 related datasets.

---

## 2. Core Python Architecture & Libraries

Unlike projects that rely on heavy external dependencies like `Faker` or `NumPy`, `scripts/generate_data.py` was deliberately built using **Python standard libraries** (`os`, `csv`, `random`, `datetime`):

| Library | Module/Class | Why Used? |
|---|---|---|
| `random` | `seed`, `choices`, `triangular`, `random` | Deterministic pseudo-random number generation with custom statistical weightings. |
| `datetime` | `date`, `datetime`, `timedelta` | Exact calendar interval calculations, leap year awareness, and date math. |
| `csv` | `writer`, `DictWriter` | High-throughput, memory-efficient streaming file generation directly to disk. |
| `os` | `path`, `makedirs` | Cross-platform directory creation and relative path resolution. |

### The Importance of the Deterministic Seed (`RANDOM_SEED = 42`)
```python
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
```
- **What it does**: Initializes the Mersenne Twister pseudo-random number generator algorithm with an exact starting state.
- **Why it matters**: Reproducibility is a non-negotiable tenet of data science. If an interviewer, hiring manager, or auditor runs `py scripts/generate_data.py` on their machine, they will generate the **exact same 10,000 users, 7,868 subscriptions, and 121,801 viewing sessions** down to the byte.

---

## 3. Step-by-Step Code Walkthrough

### 3.1 Step 1: User Demographic & Persona Modeling
```python
countries = ["United States", "United Kingdom", "Canada", "India", "Germany", "Australia"]
country_weights = [0.38, 0.18, 0.12, 0.16, 0.09, 0.07]

age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
age_weights = [0.22, 0.38, 0.22, 0.12, 0.06]

devices = ["Smart TV", "Mobile", "Laptop", "Tablet"]
device_weights = [0.42, 0.32, 0.18, 0.08]
```
- **What it does**: Assigns real-world market distributions using weighted probabilities via `random.choices(elements, weights=weights)`.
- **Logic**: 25–34 year-olds dominate OTT subscriptions (38%), Smart TVs represent the dominant living-room viewing platform (42%), followed by Mobile smartphones (32%).
- **Seasonality Simulation**: User signups are distributed across 2025 using a triangular distribution:
  ```python
  signup_day_offset = int(random.triangular(0, total_days_2025 - 1, total_days_2025 * 0.4))
  ```
  This creates a realistic peak around mid-year (summer release blockbusters).

### 3.2 Step 2: Persona-Driven Conversion & Churn Modeling
In real life, users are not identical dice rolls. StreamScope models 4 distinct **Behavioral Personas**:
1. **Power Streamer (22%)**: Heavy binge-watchers; low churn probability (12%); 22–38 sessions per month.
2. **Casual Regular (36%)**: Consistent evening watchers; moderate churn probability (28%); 10–20 sessions per month.
3. **Low Engagement (24%)**: Weekend-only casuals; high churn probability (58%); 2–7 sessions.
4. **Dormant / Trial Dropoff (18%)**: High abandonment; churn probability (85%); 0–2 sessions.

#### The Code Structure:
```python
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
```
- **Why Needed**: Simulates the realistic microeconomics where marketing channels with high acquisition costs (e.g., Social Media ads) bring higher proportions of "Dormant" and "Low Engagement" users compared to organic referrals.

### 3.3 Step 3: Subscription Lifecycle & The 30-Day True Churn Rule
A major technical achievement of StreamScope is simulating **multi-lifecycle subscriptions** (users who subscribe, cancel, wait, and reactivate):
```python
if status == "Canceled" and cur_end and cur_end < date(2025, 11, 15):
    reactivate_prob = 0.18 if persona in ["Power Streamer", "Casual Regular"] else 0.06
    if random.random() < reactivate_prob:
        gap_days = random.randint(35, 90) # True reactivation (> 30 days)
        react_start = cur_end + timedelta(days=gap_days)
```
- **Input**: User cancellation event before mid-November 2025.
- **Output**: A second distinct subscription record (`subscription_id` 2) for the same `user_id`.
- **Chronological Coherence**: Guaranteed that `react_start > cur_end` so that a user never has overlapping active subscriptions.

### 3.4 Step 4: Viewing Session Synthesis & Time-of-Day Curve
```python
hour_weights = [1]*6 + [2]*6 + [4]*6 + [8]*6 # night, morning, afternoon, evening
sess_hour = random.choices(range(24), weights=hour_weights)[0]
```
- **Peak Hours**: Sessions are heavily weighted towards 18:00 to 23:59 (evening prime-time entertainment).
- **Completion Dynamics**: A web series episode (e.g., 55 min) vs. movie (e.g., 124 min) generates completion percentage based on device:
  - Smart TV sessions average **81.4% completion**.
  - Mobile sessions average **58.2% completion** due to notifications and transit interruptions.

---

## 4. Comprehensive Audit of Numerical Constants & Hardcoded Values

Interviewers frequently ask: *"Why did you choose 10,000 users? Where did that $11.99 price come from?"*  
Use this taxonomy to classify every number in your defense:

| Parameter | Value in Code | Category | Exact Technical & Business Justification |
|---|---|---|---|
| `NUM_USERS` | `10,000` | **Technical Configuration** | Selected to provide a statistically significant sample size (> 30 samples per segment) while allowing instant in-memory SQL execution (< 1 sec) on standard laptop hardware. |
| `NUM_CONTENT` | `80` | **Demonstration Assumption** | Represents a focused catalog across 8 primary genres (10 titles each: 5 movies, 5 web series), balancing catalog breadth with visual clarity in dashboard bar charts. |
| `Observation Period` | `2025-01-01` to `2025-12-31` | **Business Definition** | Standard full 12-month calendar fiscal year for annualized churn, MRR trends, and seasonal quarter comparisons. |
| `FOLLOWUP_DATE` | `2026-01-31` | **Analytical Design** | A 30-day grace period beyond year-end. **Critical for preventing right-censoring bias**: allows users canceling on Dec 31 to be tracked for 30 days to see if they reactivate. |
| `Plan Pricing` | `$6.99, $11.99, $16.99, $21.99` | **Industry Benchmark** | Directly modeled on real-world US OTT pricing tiers (Netflix/Max: Ad-supported, Standard 1080p, Premium 4K, Multi-screen family). |
| `Annual Discount` | `18%` | **Business Assumption** | Standard SaaS/OTT retention incentive (`monthly_fee = round(monthly_fee * 0.82, 2)`). |
| `30-Day Churn Threshold` | `30 Days` | **Business Rule** | Distinguishes accidental billing failure / temporary vacation from permanent subscriber attrition. |
| `Engagement Cutoff` | `30 Hours & 20 Sessions` | **Analysis-Supported** | Empirically derived threshold in `sql/11_customer_segmentation.sql` that isolates top 20% "Power Streamers". |

---

## 5. Automated Data Validation Pipeline (`scripts/validate_data.py`)

Generating data is only half the battle. In production, raw data must pass automated validation assertions before loading into the database. StreamScope executes **22 automated assertions**:

```python
# Sample Assertion 1: Zero Overlapping Subscriptions
def test_no_overlapping_subscriptions(subs):
    subs_by_user = defaultdict(list)
    for s in subs:
        subs_by_user[s["user_id"]].append((s["start_date"], s["end_date"] or "9999-12-31"))
    for uid, intervals in subs_by_user.items():
        intervals.sort()
        for i in range(len(intervals) - 1):
            assert intervals[i][1] < intervals[i+1][0], f"Overlap detected for user {uid}"
```

### The 22 Assertions Summary:
1. **6 Row Count Bounds Checks**: Asserts row counts fall within expected generation bands.
2. **6 Primary Key Uniqueness Checks**: Confirms 0 duplicate IDs across all 6 files.
3. **5 Foreign Key Integrity Checks**: Confirms that every `user_id` and `content_id` exists in parent dimension tables.
4. **2 Chronological Coherence Checks**: Asserts `start_date >= signup_date` and `end_date >= start_date`.
5. **1 Non-Overlap Check**: Asserts zero concurrent overlapping subscriptions per user.
6. **2 Domain & Range Checks**: Asserts completion % is [0, 100], watch minutes > 0, fees > 0.

---

## 6. How to Answer Interview Questions on Data Generation

### Q: "Why didn't you just scrape real Netflix data?"
> **Strong Answer**:  
> *"Commercial streaming providers treat user-level clickstream events, individual playback completion percentages, and exact cancellation timestamps as proprietary trade secrets. Public Kaggle datasets only provide static movie catalog metadata (titles and release years), with no user interaction or subscription lifecycle data. By architecting a deterministic Python simulation engine, I was able to model full relational dependencies, user personas, and behavioral leading indicators of churn while ensuring complete reproducibility with seed 42."*

### Q: "How did you prevent synthetic data from having unrealistic bias?"
> **Strong Answer**:  
> *"I avoided uniform random distributions. Instead, I applied weighted probabilities reflecting real-world demographics (e.g., 42% Smart TV adoption), triangular distributions for registration seasonality, and persona-based conditional probabilities. For instance, users acquired via Social Media were parameterized with higher dormant probabilities than organic referrals, reflecting real customer acquisition cost and retention disparities."*
