-- =====================================================================
-- StreamScope OTT Analytics
-- Module F: Cohort Retention Analysis
-- File: sql/10_cohort_retention.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- COHORT ANALYSIS 1: User Registration Cohort Activity Retention
-- ---------------------------------------------------------------------
-- Cohort Definition: Month in which user registered on StreamScope.
-- Activity Retention: User streamed >= 1 viewing session in Month N after signup.
-- Month 0 = Signup calendar month
-- Month 1 = 1 month after signup, etc.
-- ---------------------------------------------------------------------
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
    -- Month 0
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 0 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m0_retention_pct,
    -- Month 1
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 1 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m1_retention_pct,
    -- Month 2
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 2 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m2_retention_pct,
    -- Month 3
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 3 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m3_retention_pct,
    -- Month 6
    ROUND(COUNT(DISTINCT CASE WHEN uma.month_number = 6 THEN uma.user_id END) * 100.0 / cs.cohort_user_count, 1) AS m6_retention_pct
FROM cohort_sizes cs
JOIN user_signup_cohort usc ON cs.cohort_month = usc.cohort_month
LEFT JOIN user_monthly_activity uma ON usc.user_id = uma.user_id
GROUP BY cs.cohort_month, cs.cohort_user_count
ORDER BY cs.cohort_month;

-- ---------------------------------------------------------------------
-- COHORT ANALYSIS 2: Paid Subscriber Cohort Retention
-- ---------------------------------------------------------------------
-- Cohort Definition: Month of user's first paid subscription start.
-- Subscription Retention: User continues to hold an active paid subscription in Month N.
-- ---------------------------------------------------------------------
WITH first_subscription AS (
    SELECT
        user_id,
        MIN(start_date) AS first_sub_date,
        DATE_FORMAT(MIN(start_date), '%Y-%m') AS sub_cohort_month
    FROM subscriptions
    GROUP BY user_id
),
sub_cohort_sizes AS (
    SELECT
        sub_cohort_month,
        COUNT(DISTINCT user_id) AS initial_subscribers
    FROM first_subscription
    WHERE first_sub_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY sub_cohort_month
),
sub_retention_monthly AS (
    SELECT
        fs.sub_cohort_month,
        fs.user_id,
        -- Check if user is active in Month N (where month N is evaluated at first_sub_date + N months)
        MAX(CASE WHEN s.start_date <= DATE_ADD(fs.first_sub_date, INTERVAL 0 MONTH) 
                 AND (s.end_date IS NULL OR s.end_date >= DATE_ADD(fs.first_sub_date, INTERVAL 0 MONTH)) THEN 1 ELSE 0 END) AS retained_m0,
        MAX(CASE WHEN s.start_date <= DATE_ADD(fs.first_sub_date, INTERVAL 1 MONTH) 
                 AND (s.end_date IS NULL OR s.end_date >= DATE_ADD(fs.first_sub_date, INTERVAL 1 MONTH)) THEN 1 ELSE 0 END) AS retained_m1,
        MAX(CASE WHEN s.start_date <= DATE_ADD(fs.first_sub_date, INTERVAL 2 MONTH) 
                 AND (s.end_date IS NULL OR s.end_date >= DATE_ADD(fs.first_sub_date, INTERVAL 2 MONTH)) THEN 1 ELSE 0 END) AS retained_m2,
        MAX(CASE WHEN s.start_date <= DATE_ADD(fs.first_sub_date, INTERVAL 3 MONTH) 
                 AND (s.end_date IS NULL OR s.end_date >= DATE_ADD(fs.first_sub_date, INTERVAL 3 MONTH)) THEN 1 ELSE 0 END) AS retained_m3,
        MAX(CASE WHEN s.start_date <= DATE_ADD(fs.first_sub_date, INTERVAL 6 MONTH) 
                 AND (s.end_date IS NULL OR s.end_date >= DATE_ADD(fs.first_sub_date, INTERVAL 6 MONTH)) THEN 1 ELSE 0 END) AS retained_m6
    FROM first_subscription fs
    JOIN subscriptions s ON fs.user_id = s.user_id
    GROUP BY fs.sub_cohort_month, fs.user_id
)
SELECT
    scs.sub_cohort_month,
    scs.initial_subscribers,
    ROUND(SUM(srm.retained_m0) * 100.0 / scs.initial_subscribers, 1) AS paid_m0_retention_pct,
    ROUND(SUM(srm.retained_m1) * 100.0 / scs.initial_subscribers, 1) AS paid_m1_retention_pct,
    ROUND(SUM(srm.retained_m2) * 100.0 / scs.initial_subscribers, 1) AS paid_m2_retention_pct,
    ROUND(SUM(srm.retained_m3) * 100.0 / scs.initial_subscribers, 1) AS paid_m3_retention_pct,
    ROUND(SUM(srm.retained_m6) * 100.0 / scs.initial_subscribers, 1) AS paid_m6_retention_pct
FROM sub_cohort_sizes scs
JOIN sub_retention_monthly srm ON scs.sub_cohort_month = srm.sub_cohort_month
GROUP BY scs.sub_cohort_month, scs.initial_subscribers
ORDER BY scs.sub_cohort_month;
