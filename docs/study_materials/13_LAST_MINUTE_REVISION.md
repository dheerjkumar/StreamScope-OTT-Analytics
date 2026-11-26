# Module 13: 15-Minute Pre-Interview Rapid Revision Refresher

> **File Reference:** `docs/study_materials/13_LAST_MINUTE_REVISION.md`  
> **Audience:** Candidates reviewing in the waiting room 15 minutes before an interview  
> **Objective:** Ultra-condensed cheat sheet of critical formulas, numbers, SQL syntax, and insights.

---

## 1. The 60-Second Elevator Pitch
> *"StreamScope is an end-to-end OTT analytics project tracking user engagement and subscriber churn across 10,000 users and 548K+ records. Using Python for simulation (seed 42), MySQL 8.0 for 3NF relational modeling and complex SQL (CTEs, window functions, 30-day true churn self-joins), and Power BI for a 3-page PBIR dashboard, the analysis uncovered that 68% of churned subscribers hit an 'engagement cliff' weeks prior, allowing product teams to intervene before cancellation."*

---

## 2. Key Numbers You Must Have Memorized

```
[ Total Records: 548,020 ]  -->  [ Users: 10,000 ]  -->  [ Active Subscribers: 5,717 ]
[ Total Watch Hours: 126,608.5 ]  -->  [ Sessions: 121,801 ]  -->  [ App Events: 408,267 ]
[ Active Monthly MRR: $70,261.77 ]  -->  [ ARPU: $12.29 ]  -->  [ Avg Completion: 76.34% ]
[ Seed: 42 ]  -->  [ Windows: 2025-01-01 to 2025-12-31 (Followup: 2026-01-31) ]
```

---

## 3. Core Formulas At a Glance

| Metric | Exact Mathematical Formula |
|---|---|
| **Monthly Churn Rate %** | $\frac{\text{True Churned Subscribers in Month } M}{\text{Active Subscribers at Start of Month } M} \times 100$ |
| **Subscriber Retention Rate %** | $100\% - \text{Monthly Churn Rate \%}$ |
| **DAU/MAU Stickiness %** | $\frac{\text{Average Daily Active Viewers (DAU)}}{\text{Monthly Active Viewers (MAU)}} \times 100$ |
| **Active MRR** | $\sum (\text{monthly\_fee of subscriptions where status = 'Active'})$ |
| **ARPU** | $\frac{\text{Active MRR}}{\text{Active Paid Subscribers}} = \frac{\$70,261.77}{5,717} = \mathbf{\$12.29}$ |
| **Conversion Rate %** | $\frac{\text{Converted Paying Users (7,728)}}{\text{Total Registered Users (10,000)}} \times 100 = \mathbf{77.28\%}$ |
| **Completion Rate %** | $\frac{\text{watch\_minutes}}{\text{content duration\_minutes}} \times 100$ |

---

## 4. Key SQL Concepts Implemented

```sql
-- 1. Lag Window Function for MoM Growth:
LAG(monthly_active_users, 1) OVER (ORDER BY activity_month)

-- 2. Distinguishing 1st Subscription vs Reactivation:
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY start_date ASC)

-- 3. Top Content Dense Rank:
DENSE_RANK() OVER (ORDER BY total_watch_hours DESC)

-- 4. 30-Day True Churn Self-Join:
LEFT JOIN subscriptions s2 ON s1.user_id = s2.user_id AND s2.start_date > s1.end_date
CASE WHEN MIN(s2.start_date) IS NULL OR DATEDIFF(MIN(s2.start_date), s1.end_date) > 30 THEN 1 ELSE 0 END

-- 5. Safe Division:
ROUND(churn_count * 100.0 / NULLIF(opening_count, 0), 2)
```

---

## 5. Core DAX Expressions

```dax
-- Active MRR:
Current MRR = CALCULATE(SUM(FactSubscriptions[monthly_fee]), FactSubscriptions[status] = "Active")

-- ARPU:
ARPU = DIVIDE([Current MRR], [Active Paid Subscribers], 0)

-- Total Watch Hours:
Total Watch Hours = DIVIDE(SUM(FactViewingSessions[watch_minutes]), 60, 0)
```

---

## 6. Top 3 Business Findings to Mention

1. **The Engagement Cliff**: 68.4% of churned users streamed under 60 minutes in their final 30 active days. *Recommendation: Trigger an automated re-engagement email at 12 consecutive days of zero sessions.*
2. **Channel Quality**: Referral acquisitions have 13.2% churn; Paid Social has 38.4% churn. *Recommendation: Shift 20% of paid ad budget into customer referral incentives.*
3. **Exit Friction**: 32.4% cite "Price too high" and 14.2% cite "Infrequent usage". *Recommendation: Offer a 1-click subscription pause (1–3 months) and downgrade path to Basic with Ads ($6.99).*

---

## 7. Fast Answers to Deadly Interview Trap Questions

- **"Is this real data?"** $\rightarrow$ *"Synthetic data generated via Python seed 42 to model proprietary clickstream telemetry that streaming services keep confidential."*
- **"Why not use an INNER JOIN for segments?"** $\rightarrow$ *"An INNER JOIN drops users who registered but never streamed, artificially inflating engagement metrics. A LEFT JOIN preserves all 10,000 accounts."*
- **"Why Import Mode in Power BI?"** $\rightarrow$ *"Sub-50ms VertiPaq in-memory performance and full DAX expression support across 500K records."*
- **"Why is watching 30+ hours correlated with lower churn?"** $\rightarrow$ *"High watch time doesn't cause retention; it is a symptom of high customer satisfaction. Forcing watch time via autoplay won't fix churn; improving content relevancy will."*
