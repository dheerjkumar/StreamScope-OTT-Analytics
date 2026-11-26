-- =====================================================================
-- StreamScope OTT Analytics
-- Script 12: Strategic Business Insights & Executive Synthesis
-- File: sql/12_business_insights.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- INSIGHT 1: Executive KPI Scorecard
-- ---------------------------------------------------------------------
-- Consolidates all primary business metrics into a single executive dashboard row.
-- ---------------------------------------------------------------------
SELECT
    (SELECT COUNT(*) FROM users) AS total_registered_users,
    (SELECT COUNT(DISTINCT user_id) FROM subscriptions WHERE status = 'Active') AS current_active_subscribers,
    (SELECT ROUND(COUNT(DISTINCT user_id) * 100.0 / (SELECT COUNT(*) FROM users), 2) 
     FROM subscriptions WHERE status = 'Active') AS overall_conversion_rate_pct,
    (SELECT ROUND(SUM(monthly_fee), 2) FROM subscriptions WHERE status = 'Active') AS current_active_mrr,
    (SELECT ROUND(SUM(watch_minutes) / 60.0, 1) FROM viewing_sessions) AS total_streamed_hours,
    (SELECT COUNT(*) FROM viewing_sessions) AS total_viewing_sessions,
    (SELECT ROUND(AVG(completion_percentage), 2) FROM viewing_sessions) AS avg_platform_completion_rate,
    (SELECT ROUND(COUNT(DISTINCT CASE WHEN is_true_churn = 1 THEN user_id END) * 100.0 / 
                  COUNT(DISTINCT user_id), 2) 
     FROM v_classified_cancellations) AS lifetime_subscriber_churn_rate_pct;

-- ---------------------------------------------------------------------
-- INSIGHT 2: Revenue at Risk by Churn Reason
-- ---------------------------------------------------------------------
-- Quantifies the financial impact of each friction point to prioritize product fixes.
-- ---------------------------------------------------------------------
SELECT
    cancellation_reason,
    COUNT(DISTINCT user_id) AS churned_subscribers,
    ROUND(SUM(monthly_fee), 2) AS lost_mrr,
    ROUND(SUM(monthly_fee) * 12.0, 2) AS annualized_run_rate_loss,
    ROUND(SUM(monthly_fee) * 100.0 / 
          (SELECT SUM(monthly_fee) FROM v_classified_cancellations WHERE is_true_churn = 1), 2) AS pct_of_revenue_lost
FROM v_classified_cancellations
WHERE is_true_churn = 1 AND cancellation_reason IS NOT NULL AND cancellation_reason != ''
GROUP BY cancellation_reason
ORDER BY lost_mrr DESC;

-- ---------------------------------------------------------------------
-- INSIGHT 3: Conversion Lag & Long-Term Retention
-- ---------------------------------------------------------------------
-- Hypothesis: Users who subscribe on Day 0-1 have higher retention than users who wait 4+ days.
-- ---------------------------------------------------------------------
WITH user_conversion_lag AS (
    SELECT
        u.user_id,
        DATEDIFF(MIN(s.start_date), u.signup_date) AS days_to_subscribe,
        MAX(CASE WHEN s.status = 'Active' THEN 1 ELSE 0 END) AS is_currently_active
    FROM users u
    JOIN subscriptions s ON u.user_id = s.user_id
    GROUP BY u.user_id, u.signup_date
)
SELECT
    CASE
        WHEN days_to_subscribe = 0 THEN 'Day 0 (Immediate)'
        WHEN days_to_subscribe = 1 THEN 'Day 1'
        WHEN days_to_subscribe BETWEEN 2 AND 3 THEN 'Days 2-3'
        ELSE 'Days 4+'
    END AS conversion_speed_window,
    COUNT(user_id) AS total_subscribers,
    SUM(is_currently_active) AS active_subscribers,
    ROUND(SUM(is_currently_active) * 100.0 / COUNT(user_id), 2) AS current_retention_rate_pct
FROM user_conversion_lag
GROUP BY conversion_speed_window
ORDER BY conversion_speed_window;

-- ---------------------------------------------------------------------
-- INSIGHT 4: Device Loyalty and Screen Preference by Tier
-- ---------------------------------------------------------------------
-- Analyzes whether Premium / Family subscribers actually use multi-screen / 4K devices.
-- ---------------------------------------------------------------------
SELECT
    p.plan_name,
    COUNT(DISTINCT s.user_id) AS subscribers,
    ROUND(SUM(CASE WHEN vs.device_type = 'Smart TV' THEN 1 ELSE 0 END) * 100.0 / COUNT(vs.session_id), 1) AS smart_tv_session_pct,
    ROUND(SUM(CASE WHEN vs.device_type = 'Mobile' THEN 1 ELSE 0 END) * 100.0 / COUNT(vs.session_id), 1) AS mobile_session_pct,
    ROUND(SUM(CASE WHEN vs.device_type = 'Laptop' THEN 1 ELSE 0 END) * 100.0 / COUNT(vs.session_id), 1) AS laptop_session_pct,
    ROUND(SUM(CASE WHEN vs.device_type = 'Tablet' THEN 1 ELSE 0 END) * 100.0 / COUNT(vs.session_id), 1) AS tablet_session_pct
FROM plans p
JOIN subscriptions s ON p.plan_id = s.plan_id
JOIN viewing_sessions vs ON s.user_id = vs.user_id
GROUP BY p.plan_id, p.plan_name
ORDER BY p.plan_id;
