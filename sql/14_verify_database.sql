-- =====================================================================
-- StreamScope OTT Analytics
-- Script 14: Comprehensive Database & View Verification
-- File: sql/14_verify_database.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- -------------------------------------------------------------
-- 1. INSPECT ALL TABLES AND VIEWS
-- -------------------------------------------------------------
SELECT 
    TABLE_NAME AS object_name,
    TABLE_TYPE AS object_type
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'streamscope'
ORDER BY TABLE_TYPE, TABLE_NAME;

-- -------------------------------------------------------------
-- 2. VERIFY DATA PRESERVATION (Confirm 548,000+ rows intact)
-- -------------------------------------------------------------
SELECT 'users' AS table_name, COUNT(*) AS row_count, 'Expected: 10,000' AS benchmark FROM users
UNION ALL
SELECT 'plans', COUNT(*), 'Expected: 4' FROM plans
UNION ALL
SELECT 'content', COUNT(*), 'Expected: 80' FROM content
UNION ALL
SELECT 'subscriptions', COUNT(*), 'Expected: 7,868' FROM subscriptions
UNION ALL
SELECT 'viewing_sessions', COUNT(*), 'Expected: 121,801' FROM viewing_sessions
UNION ALL
SELECT 'app_events', COUNT(*), 'Expected: 408,267' FROM app_events;

-- -------------------------------------------------------------
-- 3. TEST AND SAMPLE ALL 5 ANALYTICAL VIEWS
-- -------------------------------------------------------------
-- View 1: v_classified_cancellations (Sample & Count)
SELECT 
    'v_classified_cancellations' AS view_tested,
    COUNT(*) AS total_rows,
    SUM(is_true_churn) AS true_churn_events,
    SUM(is_subsequently_reactivated) AS reactivated_events
FROM v_classified_cancellations;

-- View 2: v_user_engagement_segments (Sample & Count)
SELECT 
    'v_user_engagement_segments' AS view_tested,
    engagement_segment,
    COUNT(*) AS user_count
FROM v_user_engagement_segments
GROUP BY engagement_segment;

-- View 3: vw_pbi_monthly_performance (Sample & Count)
SELECT 
    'vw_pbi_monthly_performance' AS view_tested,
    calendar_month,
    active_subscribers,
    estimated_mrr,
    active_viewers_mau,
    total_watch_hours,
    churned_subscribers
FROM vw_pbi_monthly_performance
LIMIT 5;

-- View 4: vw_pbi_content_dashboard (Sample & Count)
SELECT 
    'vw_pbi_content_dashboard' AS view_tested,
    title,
    genre,
    unique_viewers,
    total_watch_hours,
    avg_completion_percentage
FROM vw_pbi_content_dashboard
ORDER BY total_watch_hours DESC
LIMIT 5;

-- View 5: vw_pbi_churn_by_dimension (Sample & Count)
SELECT 
    'vw_pbi_churn_by_dimension' AS view_tested,
    plan_name,
    COUNT(*) AS total_subs,
    SUM(is_true_churn) AS true_churns
FROM vw_pbi_churn_by_dimension
GROUP BY plan_name;
