# StreamScope Advanced SQL Query Walkthrough & Technical Guide

This guide provides an in-depth, line-by-line walkthrough of the primary SQL queries powering StreamScope's business analysis. It is designed to help analysts and candidates explain SQL query execution mechanics, join strategies, and window function logic during technical interviews.

---

## 1. Query Execution Order in Relational SQL Engines

Before reviewing specific queries, remember the logical order in which MySQL processes statements:
1. `FROM` & `JOIN` (Gathers and combines tables)
2. `WHERE` (Filters rows prior to aggregation)
3. `GROUP BY` (Collapses rows into aggregate buckets)
4. `HAVING` (Filters aggregated groups)
5. `SELECT` (Computes projected expressions, scalar functions)
6. `WINDOW FUNCTIONS` (`OVER (PARTITION BY ... ORDER BY ...)`)
7. `ORDER BY` (Sorts the final projection)
8. `LIMIT` / `OFFSET` (Restricts output row count)

---

## 2. Walkthrough: Month-over-Month Registrations & Growth (`05_user_acquisition.sql`)

```sql
WITH monthly_signups AS (
    SELECT
        DATE_FORMAT(signup_date, '%Y-%m') AS signup_month,
        COUNT(user_id) AS new_registrations
    FROM users
    WHERE signup_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(signup_date, '%Y-%m')
)
SELECT
    signup_month,
    new_registrations,
    LAG(new_registrations, 1) OVER (ORDER BY signup_month) AS prior_month_registrations,
    ROUND(
        (new_registrations - LAG(new_registrations, 1) OVER (ORDER BY signup_month)) 
        / LAG(new_registrations, 1) OVER (ORDER BY signup_month) * 100.0, 
        2
    ) AS mom_growth_pct,
    SUM(new_registrations) OVER (ORDER BY signup_month) AS cumulative_registrations
FROM monthly_signups
ORDER BY signup_month;
```

### Detailed Mechanics:
- **Lines 1–8 (Common Table Expression - CTE)**:
  - `WITH monthly_signups AS (...)`: Defines an in-memory temporary result set named `monthly_signups`.
  - `DATE_FORMAT(signup_date, '%Y-%m')`: Normalizes dates into standard string year-month buckets (e.g., `'2025-01'`).
  - `COUNT(user_id)`: Counts registrations within each monthly bucket.
- **Lines 12–18 (Window Functions)**:
  - `LAG(new_registrations, 1) OVER (ORDER BY signup_month)`: Accesses the preceding row's registration value without requiring a self-join. For the first row (`'2025-01'`), it evaluates to `NULL`.
  - `(new_registrations - LAG(...)) / LAG(...) * 100.0`: Calculates the Month-over-Month percentage change.
  - `SUM(new_registrations) OVER (ORDER BY signup_month)`: A running total cumulative sum across all months to date.

---

## 3. Walkthrough: Top-of-Funnel Channel Conversion (`05_user_acquisition.sql`)

```sql
WITH user_first_sub AS (
    SELECT
        user_id,
        MIN(start_date) AS first_paid_date
    FROM subscriptions
    GROUP BY user_id
)
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS total_signups,
    COUNT(DISTINCT s.user_id) AS converted_subscribers,
    ROUND(COUNT(DISTINCT s.user_id) * 100.0 / COUNT(DISTINCT u.user_id), 2) AS conversion_rate_pct,
    ROUND(AVG(DATEDIFF(s.first_paid_date, u.signup_date)), 1) AS avg_days_to_convert
FROM users u
LEFT JOIN user_first_sub s ON u.user_id = s.user_id
GROUP BY u.acquisition_channel
ORDER BY conversion_rate_pct DESC;
```

### Detailed Mechanics:
- **Lines 1–7**: Isolates the *first* paid subscription date for each subscriber using `MIN(start_date)`, preventing duplicate counting if a user renewed or had multiple subscriptions.
- **Line 15 (`LEFT JOIN`)**: Crucial architectural decision. An `INNER JOIN` would drop non-converting users, making it impossible to calculate conversion percentage. A `LEFT JOIN` preserves all 10,000 registered users.
- **Line 12 (`COUNT(DISTINCT s.user_id)`)**: In SQL, `COUNT(column)` ignores `NULL` values. For unconverted users, `s.user_id` is `NULL`, so only successfully converted users are counted in the numerator.
- **Line 14 (`DATEDIFF(s.first_paid_date, u.signup_date)`)**: Calculates the calendar lag between initial free account creation and activation of paid streaming access.

---

## 4. Walkthrough: 30-Day True Churn Classification (`09_churn_analysis.sql`)

```sql
CREATE OR REPLACE VIEW v_classified_cancellations AS
SELECT
    s1.subscription_id,
    s1.user_id,
    s1.plan_id,
    s1.start_date,
    s1.end_date,
    s1.monthly_fee,
    s1.cancellation_reason,
    MIN(s2.start_date) AS next_sub_start_date,
    DATEDIFF(MIN(s2.start_date), s1.end_date) AS days_to_next_sub,
    CASE
        WHEN MIN(s2.start_date) IS NULL OR DATEDIFF(MIN(s2.start_date), s1.end_date) > 30 THEN 1
        ELSE 0
    END AS is_true_churn,
    CASE
        WHEN MIN(s2.start_date) IS NOT NULL AND DATEDIFF(MIN(s2.start_date), s1.end_date) > 30 THEN 1
        ELSE 0
    END AS is_subsequently_reactivated
FROM subscriptions s1
LEFT JOIN subscriptions s2 
    ON s1.user_id = s2.user_id 
    AND s2.start_date > s1.end_date
WHERE s1.status = 'Canceled' AND s1.end_date IS NOT NULL
GROUP BY s1.subscription_id, s1.user_id, s1.plan_id, s1.start_date, s1.end_date, s1.monthly_fee, s1.cancellation_reason;
```

### Detailed Mechanics:
- **The Problem**: A user may cancel a subscription on March 15 to change billing cards or upgrade plans and immediately restart on March 16. Counting this as churn would distort metrics.
- **Lines 18–20 (Self-Join with Temporal Inequality)**:
  - `FROM subscriptions s1 LEFT JOIN subscriptions s2 ON s1.user_id = s2.user_id AND s2.start_date > s1.end_date`
  - Looks ahead in time to find any *future* subscriptions initiated by the same user.
- **Lines 8–9 (`MIN(s2.start_date)`)**: Picks the earliest future start date.
- **Lines 10–13 (`CASE WHEN ...`)**:
  - If `MIN(s2.start_date) IS NULL`, the user never returned $\rightarrow$ True Churn (`1`).
  - If `DATEDIFF(...) > 30`, the user was inactive for over a month before returning $\rightarrow$ True Churn (`1`) followed by Reactivation.
  - If `DATEDIFF(...) <= 30`, the user re-subscribed within the 30-day window $\rightarrow$ Continuous Renewal (`0`).

---

## 5. Walkthrough: Opening Base Monthly Churn Rate (`09_churn_analysis.sql`)

```sql
WITH month_starts AS (
    SELECT '2025-01' AS y_m, '2025-01-01' AS m_start, '2025-01-31' AS m_end UNION ALL
    ...
),
opening_subscribers AS (
    SELECT
        ms.y_m,
        COUNT(DISTINCT s.user_id) AS opening_subscribers_count
    FROM month_starts ms
    JOIN subscriptions s 
        ON s.start_date < ms.m_start 
        AND (s.end_date IS NULL OR s.end_date >= ms.m_start)
    GROUP BY ms.y_m
),
monthly_churns AS (
    SELECT
        DATE_FORMAT(end_date, '%Y-%m') AS y_m,
        COUNT(DISTINCT user_id) AS churned_subscribers_count
    FROM v_classified_cancellations
    WHERE is_true_churn = 1 AND end_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(end_date, '%Y-%m')
)
SELECT
    ms.y_m AS calendar_month,
    os.opening_subscribers_count AS opening_subscribers,
    mc.churned_subscribers_count AS churned_subscribers,
    ROUND(mc.churned_subscribers_count * 100.0 / NULLIF(os.opening_subscribers_count, 0), 2) AS monthly_churn_rate_pct
FROM month_starts ms
LEFT JOIN opening_subscribers os ON ms.y_m = os.y_m
LEFT JOIN monthly_churns mc ON ms.y_m = mc.y_m
ORDER BY ms.y_m;
```

### Detailed Mechanics:
- **`s.start_date < ms.m_start AND (s.end_date IS NULL OR s.end_date >= ms.m_start)`**:
  - Accurately captures who was an active paying subscriber at `00:00:00` on the first day of month $M$.
  - Avoids contaminating the churn denominator with users who signed up *during* month $M$.
- **`NULLIF(os.opening_subscribers_count, 0)`**: Prevents division by zero errors during the first month if historical data is limited.

---

## 6. Walkthrough: Cohort Retention with Dynamic Time Offsets (`10_cohort_retention.sql`)

```sql
WITH user_signup_cohort AS (
    SELECT
        user_id,
        DATE_FORMAT(signup_date, '%Y-%m') AS cohort_month,
        signup_date
    FROM users
),
user_monthly_activity AS (
    SELECT DISTINCT
        vs.user_id,
        TIMESTAMPDIFF(MONTH, usc.signup_date, vs.started_at) AS month_number
    FROM viewing_sessions vs
    JOIN user_signup_cohort usc ON vs.user_id = usc.user_id
)
SELECT
    cs.cohort_month,
    cs.cohort_user_count AS cohort_size,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 0 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m0_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 1 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 2 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m2_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 3 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m3_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 6 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m6_retention_pct
...
```

### Detailed Mechanics:
- **`TIMESTAMPDIFF(MONTH, usc.signup_date, vs.started_at)`**:
  - Dynamically computes the exact calendar month offset $N$ relative to each user's personal registration date.
  - Users streaming within 30 days of signup fall into `month_number = 0`.
- **Conditional Aggregation (`COUNT(DISTINCT CASE WHEN uma.month_number = N THEN uma.user_id END)`)**:
  - Pivots the longitudinal time-series into horizontal tabular columns (`Month 0`, `Month 1`, `Month 2`, `Month 3`, `Month 6`) for direct rendering in Power BI heatmap matrices.
