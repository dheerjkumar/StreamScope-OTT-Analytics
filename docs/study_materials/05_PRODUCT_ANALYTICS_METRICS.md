# Module 05: Complete Product Analytics Metrics Handbook

> **File Reference:** `docs/study_materials/05_PRODUCT_ANALYTICS_METRICS.md`  
> **Source Scripts:** `sql/05_user_acquisition.sql` to `sql/12_business_insights.sql`, `powerbi/dax_measures.md`  
> **Audience:** Product Analysts, Growth Analysts, Data Analysts

---

## 1. Master Metric Summary Table

| Metric | Business Definition | Formula | Verified StreamScope Benchmark |
|---|---|---|---|
| **Total Registered Users** | Top-of-funnel customer accounts created | `COUNT(DISTINCT user_id)` | **10,000** |
| **Converted Paying Subscribers** | Unique users with at least 1 paid subscription | `COUNT(DISTINCT user_id WHERE status IN ('Active','Canceled'))` | **7,728 (77.28% Conversion)** |
| **Active Paid Subscribers** | Currently paying subscribers with ongoing access | `COUNT(DISTINCT user_id WHERE status = 'Active')` | **5,717** |
| **Monthly Recurring Revenue (MRR)** | Total recurring subscription run-rate per month | `SUM(monthly_fee WHERE status = 'Active')` | **$70,261.77** |
| **Average Revenue Per User (ARPU)** | Average monthly revenue per active subscriber | `Current MRR / Active Paid Subscribers` | **$12.29** |
| **Total Watch Hours** | Platform-wide streamed video consumption | `SUM(watch_minutes) / 60.0` | **126,608.5 hrs** |
| **Total Viewing Sessions** | Distinct playback sessions initiated | `COUNT(session_id)` | **121,801 sessions** |
| **Monthly Active Viewers (MAU)** | Distinct users streaming >= 1 session in a month | `COUNT(DISTINCT user_id in Month M)` | **Ranges 3,200 – 6,400 / mo** |
| **Platform Completion Rate %** | Average video duration completed by viewers | `AVG(completion_percentage)` | **76.34%** |
| **Monthly Churn Rate %** | True churned subscribers as % of opening base | `(True Churn in Month M / Opening Base M) * 100` | **~2.8% to 3.4% / month** |

---

## 2. In-Depth Metric Breakdowns

---

### 2.1 DAU, MAU, and Stickiness Ratio

#### 1. Full Form:
- **DAU**: Daily Active Users
- **MAU**: Monthly Active Users
- **Stickiness**: DAU / MAU Ratio (%)

#### 2. Definition & Purpose:
- **DAU**: Count of unique individuals who streamed at least one video in a 24-hour calendar day.
- **MAU**: Count of unique individuals who streamed at least one video across a rolling 30-day or calendar month period.
- **DAU/MAU Stickiness**: Measures **return frequency**. A stickiness of 20% means the average monthly user tunes in 6 out of 30 days (20% of 30 days).

#### 3. Formula:
$$\text{Stickiness \%} = \left( \frac{\text{Average Daily Active Users (DAU)}}{\text{Monthly Active Users (MAU)}} \right) \times 100$$

#### 4. Actual SQL Implementation (`sql/06_user_engagement.sql`):
```sql
WITH daily_active AS (
    SELECT DATE(started_at) AS session_date, DATE_FORMAT(started_at, '%Y-%m') AS year_month, COUNT(DISTINCT user_id) AS dau
    FROM viewing_sessions GROUP BY DATE(started_at), DATE_FORMAT(started_at, '%Y-%m')
),
monthly_active AS (
    SELECT DATE_FORMAT(started_at, '%Y-%m') AS year_month, COUNT(DISTINCT user_id) AS mau
    FROM viewing_sessions GROUP BY DATE_FORMAT(started_at, '%Y-%m')
)
SELECT d.year_month, ROUND(AVG(d.dau), 0) AS avg_dau, m.mau, ROUND(AVG(d.dau) * 100.0 / m.mau, 2) AS stickiness_pct
FROM daily_active d JOIN monthly_active m ON d.year_month = m.year_month
GROUP BY d.year_month, m.mau;
```

#### 5. Common Interview Mistake:
- *Mistake*: Calculating MAU by summing up all 30 DAU values.
- *Why it's wrong*: Summing DAU double-counts users who stream on multiple days. MAU **must** be a `COUNT(DISTINCT user_id)` over the entire month.

---

### 2.2 Monthly Recurring Revenue (MRR) & ARPU

#### 1. Full Form:
- **MRR**: Monthly Recurring Revenue
- **ARPU**: Average Revenue Per User

#### 2. Business Purpose:
MRR is the lifeblood of subscription economics. It excludes one-off payments and reflects guaranteed predictable revenue. ARPU tracks whether subscriber growth is driven by premium tiers ($16.99–$21.99) or discounted entry tiers ($6.99).

#### 3. Mathematical Formula:
$$\text{MRR} = \sum (\text{monthly\_fee of active subscriptions})$$
$$\text{ARPU} = \frac{\text{Total Active MRR}}{\text{Active Paid Subscribers}}$$

#### 4. StreamScope Numerical Calculation:
- **Active Paid Subscribers**: 5,717
- **Active MRR**:
  - Basic with Ads ($6.99): 1,387 subs $\times \$6.99 = \$9,695.13$
  - Standard HD ($11.99): 2,593 subs $\times \$11.99 = \$31,090.07$
  - Premium 4K ($16.99): 1,280 subs $\times \$16.99 = \$21,747.20$
  - Family Ultra ($21.99): 457 subs $\times \$21.99 = \$7,729.37$
  - **Total MRR**: **\$70,261.77**
- **ARPU**:
  $$\text{ARPU} = \frac{\$70,261.77}{5,717} = \mathbf{\$12.29}$$

#### 5. Actual DAX Implementation (`powerbi/dax_measures.md`):
```dax
Current MRR = 
CALCULATE(
    SUM(FactSubscriptions[monthly_fee]),
    FactSubscriptions[status] = "Active"
)

ARPU = 
DIVIDE([Current MRR], [Active Paid Subscribers], 0)
```

---

### 2.3 Monthly Subscriber Churn Rate %

#### 1. Definition:
The percentage of paid subscribers active at the beginning of a calendar month who permanently terminate their subscription during that month.

#### 2. Formula:
$$\text{Monthly Churn Rate \%} = \left( \frac{\text{True Churned Subscribers in Month } M}{\text{Active Subscribers at Start of Month } M} \right) \times 100$$

#### 3. Why the Denominator Matters (Common Trap):
- **Wrong Approach**: `Churn Rate = Churned Users in Month / Total Registered Users`. (Dilutes churn by counting free registered users).
- **Wrong Approach**: `Churn Rate = Churned Users / Ending Active Users`. (If 100 churned and ending users is 50, churn would be 200%).
- **Correct Industry Standard**: Opening active subscriber base (subscribers active on Day 1 of Month M).

#### 4. Actual SQL Implementation (`sql/09_churn_analysis.sql`):
```sql
SELECT
    ms.y_m AS calendar_month,
    os.opening_subscribers_count AS opening_subscribers,
    mc.churned_subscribers_count AS churned_subscribers,
    ROUND(mc.churned_subscribers_count * 100.0 / NULLIF(os.opening_subscribers_count, 0), 2) AS monthly_churn_rate_pct
FROM month_starts ms
JOIN opening_subscribers os ON ms.y_m = os.y_m
LEFT JOIN monthly_churns mc ON ms.y_m = mc.y_m;
```

---

### 2.4 Content Completion Rate %

#### 1. Definition:
The percentage of a title's runtime watched during a playback session.
$$\text{Completion Rate \%} = \left( \frac{\text{watch\_minutes}}{\text{content duration\_minutes}} \right) \times 100$$

#### 2. Product Significance:
- **Low Completion (< 30%)**: Signifies mismatched user expectations (clickbait thumbnail, poor pacing, immediate abandonment).
- **High Completion (> 75%)**: Signifies strong content engagement and satisfaction.
- **Verified StreamScope Baseline**: **76.34%** across all 121,801 sessions. Smart TV viewing achieves **81.4%**, while Mobile viewing averages **58.2%**.

---

## 3. Important Distinctions Every Analyst Must Know

### User Churn vs. Subscriber Churn:
- **User Churn (App Churn)**: A registered user stops opening the app (becomes inactive/dormant). They may not be paying.
- **Subscriber Churn**: A paying customer cancels their recurring billing agreement.
- *Key Takeaway*: User churn **precedes** subscriber churn. Users stop watching 3 weeks before they cancel their subscription.

### Subscription Retention vs. Engagement Retention:
- **Subscription Retention**: Is the user still being charged \$11.99 on the 1st of the month?
- **Engagement Retention**: Did the user actually stream video content this week?
- *Risk*: A user can have 100% subscription retention while having 0% engagement retention ("Zombie Subscriber"). When they eventually check their bank statement, they churn permanently.

### Cancellation Date vs. End Date:
- A user may click "Cancel Subscription" on January 10th.
- However, since they paid for the full month on January 1st, their subscription `end_date` is January 31st.
- In StreamScope, churn timing is tied to the **`end_date`** when platform access terminates.
