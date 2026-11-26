-- =====================================================================
-- StreamScope OTT Analytics
-- Script 04: Post-Load Data Quality & Integrity Validation
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- -------------------------------------------------------------
-- CHECK 1: Table Record Counts
-- -------------------------------------------------------------
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL
SELECT 'plans', COUNT(*) FROM plans
UNION ALL
SELECT 'content', COUNT(*) FROM content
UNION ALL
SELECT 'subscriptions', COUNT(*) FROM subscriptions
UNION ALL
SELECT 'viewing_sessions', COUNT(*) FROM viewing_sessions
UNION ALL
SELECT 'app_events', COUNT(*) FROM app_events;

-- -------------------------------------------------------------
-- CHECK 2: Primary Key Duplicate Verification (Must return 0)
-- -------------------------------------------------------------
SELECT 'Duplicate Users' AS check_item, COUNT(*) - COUNT(DISTINCT user_id) AS duplicates FROM users
UNION ALL
SELECT 'Duplicate Plans', COUNT(*) - COUNT(DISTINCT plan_id) FROM plans
UNION ALL
SELECT 'Duplicate Content', COUNT(*) - COUNT(DISTINCT content_id) FROM content
UNION ALL
SELECT 'Duplicate Subscriptions', COUNT(*) - COUNT(DISTINCT subscription_id) FROM subscriptions
UNION ALL
SELECT 'Duplicate Sessions', COUNT(*) - COUNT(DISTINCT session_id) FROM viewing_sessions
UNION ALL
SELECT 'Duplicate Events', COUNT(*) - COUNT(DISTINCT event_id) FROM app_events;

-- -------------------------------------------------------------
-- CHECK 3: Orphan Foreign Key Records (Must return 0)
-- -------------------------------------------------------------
SELECT 'Orphan Subscriptions (Invalid User)' AS issue, COUNT(*) AS count
FROM subscriptions s
LEFT JOIN users u ON s.user_id = u.user_id
WHERE u.user_id IS NULL

UNION ALL

SELECT 'Orphan Subscriptions (Invalid Plan)', COUNT(*)
FROM subscriptions s
LEFT JOIN plans p ON s.plan_id = p.plan_id
WHERE p.plan_id IS NULL

UNION ALL

SELECT 'Orphan Sessions (Invalid User)', COUNT(*)
FROM viewing_sessions vs
LEFT JOIN users u ON vs.user_id = u.user_id
WHERE u.user_id IS NULL

UNION ALL

SELECT 'Orphan Sessions (Invalid Content)', COUNT(*)
FROM viewing_sessions vs
LEFT JOIN content c ON vs.content_id = c.content_id
WHERE c.content_id IS NULL

UNION ALL

SELECT 'Orphan Events (Invalid User)', COUNT(*)
FROM app_events ae
LEFT JOIN users u ON ae.user_id = u.user_id
WHERE u.user_id IS NULL;

-- -------------------------------------------------------------
-- CHECK 4: Chronological and Date Consistency (Must return 0)
-- -------------------------------------------------------------
SELECT 'Subscription start before User Signup' AS anomaly, COUNT(*) AS count
FROM subscriptions s
JOIN users u ON s.user_id = u.user_id
WHERE s.start_date < u.signup_date

UNION ALL

SELECT 'Subscription end before start date', COUNT(*)
FROM subscriptions
WHERE end_date IS NOT NULL AND end_date < start_date

UNION ALL

SELECT 'Viewing session before user signup', COUNT(*)
FROM viewing_sessions vs
JOIN users u ON vs.user_id = u.user_id
WHERE DATE(vs.started_at) < u.signup_date;

-- -------------------------------------------------------------
-- CHECK 5: Metric Bounds and Ranges (Must return 0)
-- -------------------------------------------------------------
SELECT 'Invalid Completion Percentage (<0 or >100)' AS metric_anomaly, COUNT(*) AS count
FROM viewing_sessions
WHERE completion_percentage < 0.0 OR completion_percentage > 100.0

UNION ALL

SELECT 'Negative or Zero Watch Minutes', COUNT(*)
FROM viewing_sessions
WHERE watch_minutes <= 0

UNION ALL

SELECT 'Negative or Zero Subscription Fee', COUNT(*)
FROM subscriptions
WHERE monthly_fee <= 0;
