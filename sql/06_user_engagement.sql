-- =====================================================================
-- StreamScope OTT Analytics
-- Module B: User Engagement Analysis
-- File: sql/06_user_engagement.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- QUERY B1: Monthly Active Users (MAU), Total Watch Hours & MoM Growth
-- ---------------------------------------------------------------------
-- Business Question: What is our monthly active viewer volume and streaming volume across 2025?
-- Active User Definition: A user who completed at least one viewing session (>= 1 min) in that month.
-- Tables: viewing_sessions
-- Functions: DATE_FORMAT, COUNT(DISTINCT), SUM, ROUND, LAG()
-- ---------------------------------------------------------------------
WITH monthly_metrics AS (
    SELECT
        DATE_FORMAT(started_at, '%Y-%m') AS activity_month,
        COUNT(DISTINCT user_id) AS monthly_active_users,
        COUNT(session_id) AS total_sessions,
        ROUND(SUM(watch_minutes) / 60.0, 1) AS total_watch_hours,
        ROUND(SUM(watch_minutes) / COUNT(DISTINCT user_id), 1) AS avg_watch_minutes_per_viewer
    FROM viewing_sessions
    WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
    GROUP BY DATE_FORMAT(started_at, '%Y-%m')
)
SELECT
    activity_month,
    monthly_active_users,
    LAG(monthly_active_users, 1) OVER (ORDER BY activity_month) AS prior_mau,
    ROUND((monthly_active_users - LAG(monthly_active_users, 1) OVER (ORDER BY activity_month)) 
          * 100.0 / LAG(monthly_active_users, 1) OVER (ORDER BY activity_month), 2) AS mau_growth_pct,
    total_sessions,
    total_watch_hours,
    avg_watch_minutes_per_viewer
FROM monthly_metrics
ORDER BY activity_month;

-- ---------------------------------------------------------------------
-- QUERY B2: Platform Stickiness (DAU, MAU and DAU/MAU Ratio)
-- ---------------------------------------------------------------------
-- Business Question: How frequently do monthly viewers return to StreamScope daily?
-- Why Needed: High DAU/MAU ratio indicates daily habit formation and strong product stickiness.
-- Tables: viewing_sessions
-- Functions: DATE, DATE_FORMAT, COUNT(DISTINCT), AVG
-- ---------------------------------------------------------------------
WITH daily_active AS (
    SELECT
        DATE(started_at) AS session_date,
        DATE_FORMAT(started_at, '%Y-%m') AS year_month,
        COUNT(DISTINCT user_id) AS dau
    FROM viewing_sessions
    WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
    GROUP BY DATE(started_at), DATE_FORMAT(started_at, '%Y-%m')
),
monthly_active AS (
    SELECT
        DATE_FORMAT(started_at, '%Y-%m') AS year_month,
        COUNT(DISTINCT user_id) AS mau
    FROM viewing_sessions
    WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
    GROUP BY DATE_FORMAT(started_at, '%Y-%m')
)
SELECT
    d.year_month,
    ROUND(AVG(d.dau), 0) AS avg_daily_active_users,
    m.mau AS monthly_active_users,
    ROUND(AVG(d.dau) * 100.0 / m.mau, 2) AS dau_to_mau_stickiness_pct
FROM daily_active d
JOIN monthly_active m ON d.year_month = m.year_month
GROUP BY d.year_month, m.mau
ORDER BY d.year_month;

-- ---------------------------------------------------------------------
-- QUERY B3: Device-Wise Engagement & Completion Performance
-- ---------------------------------------------------------------------
-- Business Question: Which streaming hardware delivers the most engaged viewing experience?
-- Why Needed: Mobile streams often suffer from low completion due to distractions; Smart TVs drive long sessions.
-- Tables: viewing_sessions
-- Functions: COUNT, SUM, AVG, ROUND
-- ---------------------------------------------------------------------
SELECT
    device_type,
    COUNT(session_id) AS total_sessions,
    COUNT(DISTINCT user_id) AS unique_viewers,
    ROUND(SUM(watch_minutes) / 60.0, 1) AS total_watch_hours,
    ROUND(AVG(watch_minutes), 1) AS avg_session_duration_mins,
    ROUND(AVG(completion_percentage), 2) AS avg_completion_percentage
FROM viewing_sessions
GROUP BY device_type
ORDER BY total_watch_hours DESC;

-- ---------------------------------------------------------------------
-- QUERY B4: Day-of-Week and Prime-Time Streaming Concentration
-- ---------------------------------------------------------------------
-- Business Question: What days and hours exhibit the heaviest platform consumption?
-- Why Needed: Guides push notification scheduling and maintenance downtime windows.
-- Tables: viewing_sessions
-- Functions: DAYNAME, DAYOFWEEK, HOUR, COUNT, SUM
-- ---------------------------------------------------------------------
SELECT
    DAYNAME(started_at) AS day_of_week,
    COUNT(session_id) AS total_sessions,
    ROUND(SUM(watch_minutes) / 60.0, 1) AS total_watch_hours,
    ROUND(AVG(watch_minutes), 1) AS avg_session_watch_minutes
FROM viewing_sessions
WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
GROUP BY DAYNAME(started_at), DAYOFWEEK(started_at)
ORDER BY DAYOFWEEK(started_at);

-- ---------------------------------------------------------------------
-- QUERY B5: Hourly Prime-Time Viewing Distribution
-- ---------------------------------------------------------------------
SELECT
    HOUR(started_at) AS hour_of_day,
    COUNT(session_id) AS session_count,
    ROUND(SUM(watch_minutes) / 60.0, 1) AS total_hours_streamed,
    ROUND(COUNT(session_id) * 100.0 / (SELECT COUNT(*) FROM viewing_sessions WHERE started_at < '2026-01-01'), 2) AS pct_of_daily_streams
FROM viewing_sessions
WHERE started_at >= '2025-01-01' AND started_at < '2026-01-01'
GROUP BY HOUR(started_at)
ORDER BY hour_of_day;
