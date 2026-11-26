-- =====================================================================
-- StreamScope OTT Analytics
-- Module D: Subscription & Revenue Dynamics Analysis
-- File: sql/08_subscription_analysis.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- QUERY D1: Plan Distribution & Revenue Contribution
-- ---------------------------------------------------------------------
-- Business Question: What is the distribution of active subscribers across the 4 plan tiers, and how does each contribute to total MRR?
-- Tables: subscriptions, plans
-- ---------------------------------------------------------------------
SELECT
    p.plan_name,
    p.monthly_price,
    p.video_quality,
    COUNT(s.subscription_id) AS total_subscriptions_recorded,
    SUM(CASE WHEN s.status = 'Active' THEN 1 ELSE 0 END) AS active_subscribers,
    ROUND(SUM(CASE WHEN s.status = 'Active' THEN 1 ELSE 0 END) * 100.0 / 
          (SELECT COUNT(*) FROM subscriptions WHERE status = 'Active'), 2) AS active_subscriber_share_pct,
    ROUND(SUM(CASE WHEN s.status = 'Active' THEN s.monthly_fee ELSE 0 END), 2) AS estimated_active_mrr,
    ROUND(SUM(CASE WHEN s.status = 'Active' THEN s.monthly_fee ELSE 0 END) * 100.0 /
          (SELECT SUM(monthly_fee) FROM subscriptions WHERE status = 'Active'), 2) AS mrr_share_pct
FROM plans p
LEFT JOIN subscriptions s ON p.plan_id = s.plan_id
GROUP BY p.plan_id, p.plan_name, p.monthly_price, p.video_quality
ORDER BY estimated_active_mrr DESC;

-- ---------------------------------------------------------------------
-- QUERY D2: Monthly Subscription Lifecycle Breakdown (New, Cancellations, Reactivations)
-- ---------------------------------------------------------------------
-- Business Question: How many new subscriptions, cancellations, and reactivations happen each month?
-- Tables: subscriptions
-- ---------------------------------------------------------------------
WITH sub_order AS (
    SELECT
        subscription_id,
        user_id,
        plan_id,
        start_date,
        end_date,
        status,
        monthly_fee,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY start_date) AS sub_sequence
    FROM subscriptions
),
monthly_starts AS (
    SELECT
        DATE_FORMAT(start_date, '%Y-%m') AS month_key,
        SUM(CASE WHEN sub_sequence = 1 THEN 1 ELSE 0 END) AS new_subscribers,
        SUM(CASE WHEN sub_sequence > 1 THEN 1 ELSE 0 END) AS reactivated_subscribers,
        COUNT(subscription_id) AS total_started,
        ROUND(SUM(monthly_fee), 2) AS new_started_mrr
    FROM sub_order
    WHERE start_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(start_date, '%Y-%m')
),
monthly_cancels AS (
    SELECT
        DATE_FORMAT(end_date, '%Y-%m') AS month_key,
        COUNT(subscription_id) AS canceled_subscribers,
        ROUND(SUM(monthly_fee), 2) AS lost_mrr
    FROM subscriptions
    WHERE status = 'Canceled' AND end_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(end_date, '%Y-%m')
)
SELECT
    ms.month_key,
    ms.new_subscribers,
    ms.reactivated_subscribers,
    ms.total_started,
    COALESCE(mc.canceled_subscribers, 0) AS canceled_subscribers,
    (ms.total_started - COALESCE(mc.canceled_subscribers, 0)) AS net_subscriber_gain,
    ms.new_started_mrr,
    COALESCE(mc.lost_mrr, 0) AS lost_mrr,
    ROUND((ms.new_started_mrr - COALESCE(mc.lost_mrr, 0)), 2) AS net_mrr_movement
FROM monthly_starts ms
LEFT JOIN monthly_cancels mc ON ms.month_key = mc.month_key
ORDER BY ms.month_key;

-- ---------------------------------------------------------------------
-- QUERY D3: Estimated End-of-Month Active Subscriber Base & Run-Rate MRR
-- ---------------------------------------------------------------------
-- Business Question: What was our active paid subscriber count and recurring revenue run-rate at the end of each calendar month?
-- Active on date condition: start_date <= month_end AND (end_date IS NULL OR end_date > month_end)
-- ---------------------------------------------------------------------
WITH month_calendar AS (
    SELECT '2025-01' AS y_m, '2025-01-31' AS m_end UNION ALL
    SELECT '2025-02', '2025-02-28' UNION ALL
    SELECT '2025-03', '2025-03-31' UNION ALL
    SELECT '2025-04', '2025-04-30' UNION ALL
    SELECT '2025-05', '2025-05-31' UNION ALL
    SELECT '2025-06', '2025-06-30' UNION ALL
    SELECT '2025-07', '2025-07-31' UNION ALL
    SELECT '2025-08', '2025-08-31' UNION ALL
    SELECT '2025-09', '2025-09-30' UNION ALL
    SELECT '2025-10', '2025-10-31' UNION ALL
    SELECT '2025-11', '2025-11-30' UNION ALL
    SELECT '2025-12', '2025-12-31'
)
SELECT
    c.y_m AS calendar_month,
    COUNT(DISTINCT s.user_id) AS active_subscribers_end_of_month,
    ROUND(SUM(s.monthly_fee), 2) AS estimated_mrr,
    ROUND(AVG(s.monthly_fee), 2) AS average_revenue_per_subscriber_arpu
FROM month_calendar c
JOIN subscriptions s 
    ON s.start_date <= c.m_end 
    AND (s.end_date IS NULL OR s.end_date > c.m_end)
GROUP BY c.y_m
ORDER BY c.y_m;

-- ---------------------------------------------------------------------
-- QUERY D4: Acquisition Channel Revenue Quality (Total MRR & ARPU by Channel)
-- ---------------------------------------------------------------------
-- Business Question: Which marketing channels generate the highest lifetime revenue and average plan value?
-- ---------------------------------------------------------------------
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS total_users,
    COUNT(DISTINCT s.subscription_id) AS total_subscriptions_sold,
    ROUND(SUM(s.monthly_fee), 2) AS total_subscription_value,
    ROUND(AVG(s.monthly_fee), 2) AS avg_fee_per_subscription,
    ROUND(SUM(s.monthly_fee) / COUNT(DISTINCT u.user_id), 2) AS revenue_per_registered_user
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
GROUP BY u.acquisition_channel
ORDER BY total_subscription_value DESC;
