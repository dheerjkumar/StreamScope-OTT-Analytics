-- =====================================================================
-- StreamScope OTT Analytics
-- Module E: Churn & Cancellation Analysis
-- File: sql/09_churn_analysis.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- DEFINITION OF CHURN:
-- A paid subscriber is considered CHURNED when their paid subscription
-- access ends (end_date IS NOT NULL) AND they DO NOT start another paid
-- subscription within the following 30 days.
-- (Users renewing or restarting within <= 30 days are categorized as Continuous Renewals).
-- ---------------------------------------------------------------------

-- ---------------------------------------------------------------------
-- QUERY E1: Rigorous Identification of 30-Day True Churn Events
-- ---------------------------------------------------------------------
-- Business Question: Which canceled subscriptions represent genuine churn vs fast renewals/rebills?
-- Tables: subscriptions
-- Logic: Correlate each canceled subscription with any subsequent subscription by the same user.
-- ---------------------------------------------------------------------
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
        -- If user never started another subscription, or started after > 30 days -> True Churn
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

-- ---------------------------------------------------------------------
-- QUERY E2: Monthly Subscriber Churn Rate
-- ---------------------------------------------------------------------
-- Business Question: What is our monthly subscriber churn rate across 2025?
-- Formula: Churn Rate = (True Churned Subscribers in Month M) / (Active Subscribers at Start of Month M) * 100
-- Note: Observation follow-up period up to 2026-01-31 provides full 30-day window for all 2025 cancellations.
-- ---------------------------------------------------------------------
WITH month_starts AS (
    SELECT '2025-01' AS y_m, '2025-01-01' AS m_start, '2025-01-31' AS m_end UNION ALL
    SELECT '2025-02', '2025-02-01', '2025-02-28' UNION ALL
    SELECT '2025-03', '2025-03-01', '2025-03-31' UNION ALL
    SELECT '2025-04', '2025-04-01', '2025-04-30' UNION ALL
    SELECT '2025-05', '2025-05-01', '2025-05-31' UNION ALL
    SELECT '2025-06', '2025-06-01', '2025-06-30' UNION ALL
    SELECT '2025-07', '2025-07-01', '2025-07-31' UNION ALL
    SELECT '2025-08', '2025-08-01', '2025-08-31' UNION ALL
    SELECT '2025-09', '2025-09-01', '2025-09-30' UNION ALL
    SELECT '2025-10', '2025-10-01', '2025-10-31' UNION ALL
    SELECT '2025-11', '2025-11-01', '2025-11-30' UNION ALL
    SELECT '2025-12', '2025-12-01', '2025-12-31'
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
        COUNT(DISTINCT user_id) AS churned_subscribers_count,
        ROUND(SUM(monthly_fee), 2) AS churned_mrr
    FROM v_classified_cancellations
    WHERE is_true_churn = 1 AND end_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(end_date, '%Y-%m')
)
SELECT
    ms.y_m AS calendar_month,
    COALESCE(os.opening_subscribers_count, 0) AS opening_subscribers,
    COALESCE(mc.churned_subscribers_count, 0) AS churned_subscribers,
    COALESCE(mc.churned_mrr, 0) AS lost_recurring_revenue,
    ROUND(
        COALESCE(mc.churned_subscribers_count, 0) * 100.0 / NULLIF(os.opening_subscribers_count, 0), 
        2
    ) AS monthly_churn_rate_pct
FROM month_starts ms
LEFT JOIN opening_subscribers os ON ms.y_m = os.y_m
LEFT JOIN monthly_churns mc ON ms.y_m = mc.y_m
ORDER BY ms.y_m;

-- ---------------------------------------------------------------------
-- QUERY E3: Plan-Wise Churn Rate
-- ---------------------------------------------------------------------
-- Business Question: Are higher-priced tiers experiencing higher churn, or does entry-level ad-tier have lower commitment?
-- ---------------------------------------------------------------------
SELECT
    p.plan_name,
    p.monthly_price,
    COUNT(s.subscription_id) AS total_subscriptions,
    SUM(CASE WHEN vc.is_true_churn = 1 THEN 1 ELSE 0 END) AS churned_subscriptions,
    ROUND(
        SUM(CASE WHEN vc.is_true_churn = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(s.subscription_id), 
        2
    ) AS plan_churn_rate_pct
FROM plans p
JOIN subscriptions s ON p.plan_id = s.plan_id
LEFT JOIN v_classified_cancellations vc ON s.subscription_id = vc.subscription_id
GROUP BY p.plan_id, p.plan_name, p.monthly_price
ORDER BY plan_churn_rate_pct DESC;

-- ---------------------------------------------------------------------
-- QUERY E4: Acquisition Channel Churn Quality
-- ---------------------------------------------------------------------
-- Business Question: Which marketing channels deliver durable customers vs fast churners?
-- ---------------------------------------------------------------------
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT s.user_id) AS acquired_paid_users,
    COUNT(DISTINCT CASE WHEN vc.is_true_churn = 1 THEN s.user_id END) AS churned_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN vc.is_true_churn = 1 THEN s.user_id END) * 100.0 
        / COUNT(DISTINCT s.user_id), 
        2
    ) AS channel_churn_rate_pct
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
LEFT JOIN v_classified_cancellations vc ON s.subscription_id = vc.subscription_id
GROUP BY u.acquisition_channel
ORDER BY channel_churn_rate_pct ASC;

-- ---------------------------------------------------------------------
-- QUERY E5: Stated Cancellation Reasons Breakdown
-- ---------------------------------------------------------------------
-- Business Question: What primary reasons do churned users report upon cancellation?
-- ---------------------------------------------------------------------
SELECT
    cancellation_reason,
    COUNT(*) AS cancellation_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM v_classified_cancellations WHERE is_true_churn = 1), 2) AS pct_of_reasons,
    ROUND(SUM(monthly_fee), 2) AS lost_monthly_fee
FROM v_classified_cancellations
WHERE is_true_churn = 1 AND cancellation_reason IS NOT NULL AND cancellation_reason != ''
GROUP BY cancellation_reason
ORDER BY cancellation_count DESC;

-- ---------------------------------------------------------------------
-- QUERY E6: Engagement Cliff: Pre-Cancellation Viewing Behavior
-- ---------------------------------------------------------------------
-- Business Question: Does viewing consumption drop significantly in the 30 days prior to cancellation?
-- Why Needed: Confirms whether inactivity is a reliable early warning indicator for churn prediction.
-- ---------------------------------------------------------------------
WITH user_30d_pre_cancel_viewing AS (
    SELECT
        vc.user_id,
        vc.subscription_id,
        vc.end_date,
        COALESCE(SUM(vs.watch_minutes), 0) AS total_pre_cancel_watch_mins,
        COUNT(vs.session_id) AS total_pre_cancel_sessions
    FROM v_classified_cancellations vc
    LEFT JOIN viewing_sessions vs 
        ON vc.user_id = vs.user_id 
        AND vs.started_at >= DATE_SUB(vc.end_date, INTERVAL 30 DAY)
        AND vs.started_at <= vc.end_date
    WHERE vc.is_true_churn = 1
    GROUP BY vc.user_id, vc.subscription_id, vc.end_date
)
SELECT
    CASE
        WHEN total_pre_cancel_watch_mins = 0 THEN '0 Mins (Completely Inactive)'
        WHEN total_pre_cancel_watch_mins < 60 THEN '1-59 Mins (< 1 Hour)'
        WHEN total_pre_cancel_watch_mins < 180 THEN '60-179 Mins (1-3 Hours)'
        ELSE '180+ Mins (> 3 Hours)'
    END AS pre_cancel_activity_bucket,
    COUNT(user_id) AS churned_users_count,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM user_30d_pre_cancel_viewing), 2) AS pct_of_churned_users,
    ROUND(AVG(total_pre_cancel_watch_mins), 1) AS avg_watch_minutes
FROM user_30d_pre_cancel_viewing
GROUP BY pre_cancel_activity_bucket
ORDER BY churned_users_count DESC;

-- ---------------------------------------------------------------------
-- QUERY E7: Subscriber Reactivation Analysis
-- ---------------------------------------------------------------------
-- Business Question: What percentage of churned users return after >30 days, and what is the average dormant gap?
-- ---------------------------------------------------------------------
SELECT
    COUNT(*) AS total_true_churn_events,
    SUM(is_subsequently_reactivated) AS reactivated_events,
    ROUND(SUM(is_subsequently_reactivated) * 100.0 / COUNT(*), 2) AS reactivation_rate_pct,
    ROUND(AVG(CASE WHEN is_subsequently_reactivated = 1 THEN days_to_next_sub END), 1) AS avg_dormant_days_before_return
FROM v_classified_cancellations
WHERE is_true_churn = 1;
