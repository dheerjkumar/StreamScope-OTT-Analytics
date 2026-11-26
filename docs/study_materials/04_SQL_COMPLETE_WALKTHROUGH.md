# Module 04: Complete SQL Query Walkthrough & Technical Interview Playbook

> **File Reference:** `docs/study_materials/04_SQL_COMPLETE_WALKTHROUGH.md`  
> **Source Directory:** `sql/04_data_quality_checks.sql` to `sql/13_create_views.sql`  
> **Audience:** SQL Developers, Data Analysts, Product Analysts

---

## 1. Overview of Implemented SQL Techniques

Every SQL technique discussed here is **actually implemented** in the production scripts of this project:

| SQL Concept | Implemented In | Production Purpose |
|---|---|---|
| **Common Table Expressions (CTEs)** | `06`, `07`, `08`, `09`, `10`, `11`, `13` | Multi-step pipeline modularity, month spine generation, cohort tracking. |
| **Window: `LAG()`** | `sql/06_user_engagement.sql` | Month-over-Month (MoM) active viewer growth calculations. |
| **Window: `ROW_NUMBER()`** | `sql/08_subscription_analysis.sql` | Partitioning subscriptions per user to distinguish 1st signup vs. reactivation. |
| **Window: `DENSE_RANK()`** | `sql/07_content_analysis.sql` | Ranking top content by watch hours without skipping rank numbers on ties. |
| **Self-Join (`s1 LEFT JOIN s2`)** | `sql/09_churn_analysis.sql` | Correlating canceled subscriptions with subsequent subscriptions for 30-day True Churn. |
| **Conditional Aggregation (`CASE WHEN`)** | `08`, `09`, `10`, `11`, `13` | Pivot cohort retention tables from rows into columns (M0, M1, M2, M3, M6). |
| **Date Arithmetic (`TIMESTAMPDIFF`, `DATEDIFF`)** | `sql/09_churn_analysis.sql`, `sql/10_cohort_retention.sql` | Calculating exact tenure gaps and elapsed months between signup and stream events. |
| **Views (`CREATE OR REPLACE VIEW`)** | `sql/13_create_views.sql` | Exposing clean analytical reporting layers for Power BI consumption. |

---

## 2. In-Depth Walkthrough of Core Production Queries

### 2.1 Query 1: The 30-Day True Churn Rule (`sql/09_churn_analysis.sql` & `sql/13_create_views.sql`)

#### The Actual SQL Code:
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

#### Line-by-Line Breakdown:
1. `CREATE OR REPLACE VIEW v_classified_cancellations`: Materializes this logic as a reusable base view without duplicating storage.
2. `FROM subscriptions s1 LEFT JOIN subscriptions s2`: **Self-Join**. `s1` represents the canceled subscription. `s2` represents any future subscription by the same user.
3. `ON s1.user_id = s2.user_id AND s2.start_date > s1.end_date`: Ensures we only look for subscriptions starting **after** the cancellation date.
4. `MIN(s2.start_date)`: Finds the immediate next subscription start date. If the user never returned, this returns `NULL`.
5. `DATEDIFF(MIN(s2.start_date), s1.end_date)`: Computes the calendar gap in days between cancellation and restart.
6. `CASE WHEN ... > 30 THEN 1 ELSE 0 END AS is_true_churn`: The business rule! If `MIN(s2.start_date)` is `NULL` (never returned) OR the gap was > 30 days, it is **True Churn**. If they restarted within 1–30 days, `is_true_churn = 0` (rebill/short pause).

#### Business Value:
In real OTT businesses, ~15–20% of cancellations are involuntary (expired cards, banking failure). Treating temporary lapses as churn overstates churn rates and ruins LTV models.

---

### 2.2 Query 2: Multi-Cohort Retention Heatmap Matrix (`sql/10_cohort_retention.sql`)

#### The Actual SQL Code:
```sql
WITH user_signup_cohort AS (
    SELECT
        user_id,
        DATE_FORMAT(signup_date, '%Y-%m') AS cohort_month,
        signup_date
    FROM users
    WHERE signup_date BETWEEN '2025-01-01' AND '2025-12-31'
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS cohort_user_count
    FROM user_signup_cohort
    GROUP BY cohort_month
),
user_monthly_activity AS (
    SELECT DISTINCT
        vs.user_id,
        TIMESTAMPDIFF(MONTH, usc.signup_date, vs.started_at) AS month_number
    FROM viewing_sessions vs
    JOIN user_signup_cohort usc ON vs.user_id = usc.user_id
    WHERE vs.started_at >= '2025-01-01' AND vs.started_at <= '2026-01-31'
)
SELECT
    cs.cohort_month,
    cs.cohort_user_count AS cohort_size,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 0 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m0_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 1 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m1_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 2 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m2_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 3 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m3_retention_pct,
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 6 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m6_retention_pct
FROM cohort_sizes cs
JOIN user_signup_cohort usc ON cs.cohort_month = usc.cohort_month
LEFT JOIN user_monthly_activity uma ON usc.user_id = uma.user_id
GROUP BY cs.cohort_month, cs.cohort_user_count
ORDER BY cs.cohort_month;
```

#### Key Technical Concepts Demonstrated:
1. **`TIMESTAMPDIFF(MONTH, date1, date2)`**: Dynamically computes elapsed calendar months regardless of differing days in a month.
2. **Conditional Count Pivoting**: Instead of producing tall rows (`cohort, month_num, users`), `COUNT(DISTINCT CASE WHEN uma.month_number = N THEN uma.user_id END)` pivots the data into an executive heatmap matrix (M0 to M6).
3. **Denominator Anchoring**: Dividing by `cs.cohort_user_count` guarantees the retention rate is strictly bounded between 0% and 100%.

---

### 2.3 Query 3: Identifying Reactivations vs. First Subscriptions (`sql/08_subscription_analysis.sql`)

#### The Actual SQL Code:
```sql
WITH sub_order AS (
    SELECT
        subscription_id,
        user_id,
        plan_id,
        start_date,
        monthly_fee,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY start_date ASC) AS sub_sequence
    FROM subscriptions
)
SELECT
    DATE_FORMAT(start_date, '%Y-%m') AS month_key,
    SUM(CASE WHEN sub_sequence = 1 THEN 1 ELSE 0 END) AS new_subscribers,
    SUM(CASE WHEN sub_sequence > 1 THEN 1 ELSE 0 END) AS reactivated_subscribers,
    COUNT(subscription_id) AS total_started,
    ROUND(SUM(monthly_fee), 2) AS new_started_mrr
FROM sub_order
WHERE start_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY DATE_FORMAT(start_date, '%Y-%m')
ORDER BY month_key;
```

#### Why `ROW_NUMBER() OVER (PARTITION BY ...)` is Essential:
- `PARTITION BY user_id`: Resets the counter for each distinct user.
- `ORDER BY start_date ASC`: Assigns `sub_sequence = 1` strictly to the user's first-ever subscription. Any subsequent row receives `sub_sequence = 2, 3...`.
- In the outer query, `sub_sequence = 1` counts **New User Acquisition**, while `sub_sequence > 1` counts **Reactivations**.

---

### 2.4 Query 4: Month-over-Month (MoM) Growth with `LAG()` (`sql/06_user_engagement.sql`)

```sql
WITH monthly_metrics AS (
    SELECT
        DATE_FORMAT(started_at, '%Y-%m') AS activity_month,
        COUNT(DISTINCT user_id) AS monthly_active_users,
        ROUND(SUM(watch_minutes) / 60.0, 1) AS total_watch_hours
    FROM viewing_sessions
    WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
    GROUP BY DATE_FORMAT(started_at, '%Y-%m')
)
SELECT
    activity_month,
    monthly_active_users,
    LAG(monthly_active_users, 1) OVER (ORDER BY activity_month) AS prior_mau,
    ROUND(
        (monthly_active_users - LAG(monthly_active_users, 1) OVER (ORDER BY activity_month)) * 100.0 /
        LAG(monthly_active_users, 1) OVER (ORDER BY activity_month), 
        2
    ) AS mau_growth_pct,
    total_watch_hours
FROM monthly_metrics
ORDER BY activity_month;
```

#### Concept:
`LAG(column, offset) OVER (ORDER BY ...)` fetches the value from the preceding row without performing a costly self-join. If there is no previous month (e.g., January 2025), `prior_mau` evaluates to `NULL`.

---

## 3. Top 8 Technical SQL Interview Questions & Model Answers

### Q1: "Why use a CTE (`WITH`) instead of a subquery?"
> **Answer**:  
> *"CTEs improve code readability, maintainability, and reusability. A subquery in the `FROM` or `WHERE` clause nests logic deeply, making debugging difficult. With CTEs, each transformation step is declared sequentially from top to bottom (like functions in Python). Furthermore, in MySQL 8.0, the optimizer can materialize CTEs or fold them inline depending on cost, avoiding repeated subquery evaluations."*

### Q2: "What is the difference between `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()`?"
> **Answer**:  
> *"Imagine two titles tie for 2nd place with 5,000 hours:  
> - `ROW_NUMBER()` assigns arbitrary unique sequential integers: `1, 2, 3, 4`.  
> - `RANK()` assigns identical ranks to ties but skips subsequent ranks: `1, 2, 2, 4` (rank 3 is skipped).  
> - `DENSE_RANK()` assigns identical ranks to ties without skipping: `1, 2, 2, 3`.  
> In StreamScope (`sql/07_content_analysis.sql`), I used `DENSE_RANK()` so that executive top-10 lists do not skip rank positions when titles share identical streaming hours."*

### Q3: "What is the difference between `WHERE` and `HAVING`?"
> **Answer**:  
> *"`WHERE` filters individual rows **before** aggregation and cannot access aggregate functions (`SUM`, `AVG`). `HAVING` filters grouped summary rows **after** `GROUP BY` has executed. For instance, `WHERE status = 'Active'` filters active rows before grouping, whereas `HAVING SUM(watch_minutes) > 600` filters user groups after computing their total watch time."*

### Q4: "Why did you use a `LEFT JOIN` in `v_user_engagement_segments`?"
> **Answer**:  
> *"In `sql/11_customer_segmentation.sql`, I joined `users u LEFT JOIN viewing_sessions vs`. If I had used an `INNER JOIN`, users who signed up but never streamed a single session would have been completely dropped from the query. A `LEFT JOIN` preserves all 10,000 users, assigning `NULL` to viewing sessions, which `COALESCE` converts to 0 hours, correctly classifying them into the 'Inactive' segment."*

### Q5: "How does `PARTITION BY` differ from `GROUP BY`?"
> **Answer**:  
> *"`GROUP BY` collapses multiple rows into a single summary row per group (reducing the total row count). `PARTITION BY` is used inside window functions (`OVER (PARTITION BY ...)`): it groups rows to compute an aggregate or rank while **preserving every original row** in the result set."*

### Q6: "How do duplicate rows affect analytical calculations?"
> **Answer**:  
> *"Duplicates inflate volume metrics (`COUNT`, `SUM`). For example, if a user has two subscription records due to a bad join, `COUNT(user_id)` would count them twice, skewing conversion rates. In StreamScope, I consistently use `COUNT(DISTINCT user_id)` and verified 0 duplicate primary keys in `scripts/validate_data.py` to ensure exact metric fidelity."*

### Q7: "How would you optimize a slow-running SQL query in MySQL?"
> **Answer**:  
> *"1. Run `EXPLAIN ANALYZE <query>` to inspect the execution plan and check for full table scans (`type: ALL`).  
> 2. Ensure join and filter predicates utilize BTREE indexes (e.g., in StreamScope, composite index `(user_id, started_at)` on `viewing_sessions`).  
> 3. Avoid applying functions to indexed columns in `WHERE` clauses (e.g., write `started_at >= '2025-01-01'` instead of `YEAR(started_at) = 2025`, which disables sargability).  
> 4. Filter early inside CTEs before performing heavy joins."*

### Q8: "Why did you use `NULLIF(denominator, 0)` in churn rate queries?"
> **Answer**:  
> *"In SQL, dividing by zero causes a fatal runtime error (`Division by zero`). Wrapping the denominator in `NULLIF(os.opening_subscribers_count, 0)` converts zero to `NULL`, causing SQL to safely return `NULL` instead of crashing the batch ETL pipeline."*
