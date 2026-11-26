-- =====================================================================
-- StreamScope OTT Analytics
-- Script 13: Dedicated Power BI & Reporting Analytical Views
-- File: sql/13_create_views.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- -------------------------------------------------------------
-- VIEW 1: vw_pbi_monthly_performance
-- Feeds Dashboard 1 (Executive Overview) monthly trend visuals
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_pbi_monthly_performance AS
WITH month_spine AS (
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
signups AS (
    SELECT DATE_FORMAT(signup_date, '%Y-%m') AS y_m, COUNT(*) AS new_registrations
    FROM users
    GROUP BY DATE_FORMAT(signup_date, '%Y-%m')
),
views AS (
    SELECT
        DATE_FORMAT(started_at, '%Y-%m') AS y_m,
        COUNT(DISTINCT user_id) AS active_viewers_mau,
        COUNT(session_id) AS total_sessions,
        ROUND(SUM(watch_minutes) / 60.0, 1) AS total_watch_hours
    FROM viewing_sessions
    GROUP BY DATE_FORMAT(started_at, '%Y-%m')
),
eom_subs AS (
    SELECT
        ms.y_m,
        COUNT(DISTINCT s.user_id) AS active_subscribers,
        ROUND(SUM(s.monthly_fee), 2) AS estimated_mrr
    FROM month_spine ms
    JOIN subscriptions s 
        ON s.start_date <= ms.m_end 
        AND (s.end_date IS NULL OR s.end_date > ms.m_end)
    GROUP BY ms.y_m
),
churns AS (
    SELECT
        DATE_FORMAT(end_date, '%Y-%m') AS y_m,
        COUNT(DISTINCT user_id) AS churned_subscribers,
        ROUND(SUM(monthly_fee), 2) AS lost_mrr
    FROM v_classified_cancellations
    WHERE is_true_churn = 1
    GROUP BY DATE_FORMAT(end_date, '%Y-%m')
)
SELECT
    ms.y_m AS calendar_month,
    COALESCE(s.new_registrations, 0) AS new_registrations,
    COALESCE(es.active_subscribers, 0) AS active_subscribers,
    COALESCE(es.estimated_mrr, 0) AS estimated_mrr,
    COALESCE(v.active_viewers_mau, 0) AS active_viewers_mau,
    COALESCE(v.total_sessions, 0) AS total_sessions,
    COALESCE(v.total_watch_hours, 0) AS total_watch_hours,
    COALESCE(c.churned_subscribers, 0) AS churned_subscribers,
    COALESCE(c.lost_mrr, 0) AS lost_mrr
FROM month_spine ms
LEFT JOIN signups s ON ms.y_m = s.y_m
LEFT JOIN eom_subs es ON ms.y_m = es.y_m
LEFT JOIN views v ON ms.y_m = v.y_m
LEFT JOIN churns c ON ms.y_m = c.y_m
ORDER BY ms.y_m;

-- -------------------------------------------------------------
-- VIEW 2: vw_pbi_content_dashboard
-- Feeds Dashboard 2 (Content & Engagement)
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_pbi_content_dashboard AS
SELECT
    c.content_id,
    c.title,
    c.genre,
    c.release_year,
    c.content_type,
    c.duration_minutes,
    COUNT(DISTINCT vs.user_id) AS unique_viewers,
    COUNT(vs.session_id) AS total_plays,
    ROUND(SUM(vs.watch_minutes) / 60.0, 1) AS total_watch_hours,
    ROUND(AVG(vs.completion_percentage), 2) AS avg_completion_percentage
FROM content c
LEFT JOIN viewing_sessions vs ON c.content_id = vs.content_id
GROUP BY c.content_id, c.title, c.genre, c.release_year, c.content_type, c.duration_minutes;

-- -------------------------------------------------------------
-- VIEW 3: vw_pbi_churn_by_dimension
-- Feeds Dashboard 3 (Retention & Churn)
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW vw_pbi_churn_by_dimension AS
SELECT
    s.subscription_id,
    s.user_id,
    u.country,
    u.acquisition_channel,
    u.preferred_device,
    p.plan_name,
    p.monthly_price,
    s.start_date,
    s.end_date,
    s.status,
    s.billing_cycle,
    s.monthly_fee,
    s.cancellation_reason,
    COALESCE(vc.is_true_churn, 0) AS is_true_churn,
    COALESCE(vc.is_subsequently_reactivated, 0) AS is_reactivated
FROM subscriptions s
JOIN users u ON s.user_id = u.user_id
JOIN plans p ON s.plan_id = p.plan_id
LEFT JOIN v_classified_cancellations vc ON s.subscription_id = vc.subscription_id;

SELECT 'All reporting views created successfully.' AS status;
