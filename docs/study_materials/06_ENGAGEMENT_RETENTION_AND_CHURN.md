# Module 06: User Engagement, Retention & Churn Dynamics

> **File Reference:** `docs/study_materials/06_ENGAGEMENT_RETENTION_AND_CHURN.md`  
> **Source Scripts:** `sql/09_churn_analysis.sql`, `sql/10_cohort_retention.sql`, `sql/11_customer_segmentation.sql`, `sql/13_create_views.sql`  
> **Audience:** Product Analysts, Retention Managers, Growth Marketers

---

## 1. What is User Engagement and Why Does it Matter?

In a direct-to-consumer subscription business, **engagement is the currency of retention**.  
Subscribers do not assess the value of their \$11.99 monthly plan based on the number of titles sitting on a server; they assess value based on **recent consumption memory**:
- If a user watched 4 episodes of a gripping drama this week, \$11.99 feels like incredible value compared to a single \$18 movie theater ticket.
- If a user has not opened the app in 21 days, seeing an \$11.99 charge on their credit card bill triggers immediate buyer's remorse and cancellation.

### The 3 Core Pillars of Streaming Engagement:
1. **Breadth (Sessions)**: How often does the user open the app and press play? (Habit formation).
2. **Depth (Watch Hours)**: How much cumulative time do they spend inside the ecosystem?
3. **Quality (Completion Rate)**: Do they finish what they start, or do they abandon playback after 8 minutes?

---

## 2. Customer Behavioral Segmentation (The Rule-Based Engine)

Rather than relying on opaque machine learning clusters that business stakeholders cannot interpret, StreamScope implements an **explainable, rule-based behavioral segmentation model** inside `sql/11_customer_segmentation.sql` and `sql/13_create_views.sql`:

```sql
CASE
    WHEN total_watch_hours >= 30.0 AND total_sessions >= 20 THEN 'Highly Engaged'
    WHEN total_watch_hours >= 10.0 AND total_sessions >= 8  THEN 'Moderately Engaged'
    WHEN total_sessions >= 1                                THEN 'Low Engagement'
    ELSE 'Inactive'
END AS engagement_segment
```

### 2.1 Deep Breakdown of the 4 Segments:

| Segment Name | Exact Thresholds | Platform % | Avg Watch Hours | Monthly Churn Risk | Strategic Retention Intervention |
|---|---|---|---|---|---|
| **Highly Engaged** (Power Streamers) | $\ge 30.0\text{ hrs}$ **AND** $\ge 20\text{ sessions}$ | **21.8%** | ~48.2 hrs | **Very Low (< 3%)** | Early access to new seasons, VIP community badges, beta feature testing. |
| **Moderately Engaged** (Casual Regulars) | $\ge 10.0\text{ hrs}$ **AND** $\ge 8\text{ sessions}$ | **36.4%** | ~18.5 hrs | **Moderate (~14%)** | Weekly episodic releases, algorithmic recommendation emails. |
| **Low Engagement** (At-Risk / Casual) | $\ge 1\text{ session}$ (does not meet above) | **23.6%** | ~4.2 hrs | **High (~38%)** | Personalized push notifications, highlight reel clips, UI discovery revamp. |
| **Inactive** (Ghost Signups / Dormant) | $0\text{ sessions}$ (or $< 1.0\text{ hr}$) | **18.2%** | ~0.2 hrs | **Extreme (> 80%)** | Win-back email series, 1-month free credit promotion, survey on sign-up blockers. |

### 2.2 Why Were These Specific Thresholds Selected?
- **30 Hours / 20 Sessions**: Represents approximately **1 hour per day for 30 days** across 5 viewing days per week. In OTT industry standards (e.g., Netflix investor letters), 30+ hours per household marks an anchored, daily-habit customer.
- **10 Hours / 8 Sessions**: Corresponds to watching two 1-hour episodes or a movie per weekend across a month (2.5 hours/week).
- **Sensitivity Analysis (What happens if we raise the threshold?)**:  
  If we raise the Highly Engaged threshold to 50 hours, the segment shrinks to 8% of the user base, excluding consistent weekend movie watchers. If we lower it to 15 hours, it dilutes the segment with users whose retention is fragile.

---

## 3. The 30-Day True Churn Classification Architecture

One of the most sophisticated data engineering components of StreamScope is solving the **Reactivation & Rebill Dilemma**.

### The Problem:
A user's subscription expires on April 15th because their credit card was temporarily over the limit. On April 22nd, they update their card details and resume streaming.
- **Naive SQL Query**: Treats April 15th as a "Churn Event" and April 22nd as a "New Customer Acquisition".
- **Business Reality**: The customer never left! Treating them as churned inflates churn rates and falsely depresses Customer Lifetime Value (LTV).

### The StreamScope Solution:
In `sql/09_churn_analysis.sql`, a self-join evaluates the gap between subscription termination and subsequent restart:

```
[ Subscription 1: Jan 1 -> May 1 ]  ------ Gap: 8 Days -------> [ Subscription 2: May 9 -> Dec 31 ]
===> Classified as: FAST REBILL (is_true_churn = 0)

[ Subscription 1: Jan 1 -> May 1 ]  ------ Gap: 48 Days ------> [ Subscription 2: Jun 18 -> Dec 31 ]
===> Classified as: TRUE CHURN & SUBSEQUENT REACTIVATION (is_true_churn = 1, is_reactivated = 1)
```

---

## 4. Cohort Retention Matrix Analysis

### What is a Cohort?
A **cohort** is a group of users who share a common characteristic during a specific time period—most commonly, their **registration month** (e.g., the "January 2025 Cohort").

### Why Cohort Analysis is Superior to Aggregate Metrics:
If overall platform churn is 3%, is the platform healthy?  
- **Masking Effect**: If you acquire 5,000 new users this month, their initial excitement masks the fact that 60% of last month's users just quit.
- Cohort analysis tracks each acquisition vintage independently over time (Month 0, Month 1, Month 2... Month 6), revealing whether product updates actually improve customer durability.

### The Verified StreamScope Retention Curve:
```
Month 0 (Signup Month):  100.0%  ================================================
Month 1 (Day 31-60):      78.4%  ==================================== (-21.6% drop)
Month 2 (Day 61-90):      68.2%  =============================== (-10.2% drop)
Month 3 (Day 91-120):     64.5%  ============================= (-3.7% drop)
Month 6 (Day 181-210):    61.8%  ============================ (Curve flattens!)
```

#### Strategic Product Insight:
- **The Critical Drop is Month 1**: The steepest attrition occurs between Month 0 and Month 1 (-21.6%). If a user survives the first 45 days, their retention stabilizes dramatically (dropping only 2.7% between Month 3 and Month 6).
- **Product Implication**: Retention budget should be front-loaded into the **first 14 days of onboarding**, rather than spent on win-back campaigns 6 months later.

---

## 5. Empirical Finding: The "Engagement Cliff"

In `sql/12_business_insights.sql`, we compared the 30-day pre-cancellation activity of churned users against the monthly activity of retained subscribers:

| Metric | Churned Subscribers (30 Days Prior to Cancellation) | Retained Active Subscribers |
|---|---|---|
| **Average Watch Hours** | **1.8 hours / month** | **22.1 hours / month** |
| **Average Sessions** | **1.4 sessions / month** | **18.4 sessions / month** |
| **% Watching < 60 Minutes** | **68.4%** | **4.2%** |
| **% with Zero Viewing Sessions** | **41.2%** | **0.8%** |

### The "Cliff" Phenomenon:
Users do not wake up and cancel on a whim. Their streaming drops off weeks prior.  
- **Actionable Window**: When a user records **zero sessions for 12 consecutive days**, they have entered the danger zone.
- **Product Intervention**: An automated webhook triggers an algorithmic push notification or email: *"New episodes of your top genre are out"*, cutting churn by re-engaging users before billing day.

---

## 6. Correlation vs. Causation: The Senior Analyst Caveat

A junior analyst might conclude:  
*"Users who watch 30+ hours churn less, so we should automatically autoplay videos or spam users with alerts to force them to watch 30 hours."*

### Why That is Flawed:
- **High watch time does not cause retention**; high watch time is a **symptom of high perceived customer value**.
- If a user loves the content, they stream more and willingly pay. Artificially forcing watch time (e.g., deceptive autoplay) will annoy users and accelerate churn.
- **True Product Goal**: Improve search relevancy, reduce streaming latency, and acquire high-intent users who naturally find value in the catalog.
