-- =====================================================================
-- StreamScope OTT Analytics
-- Module G: Customer Behavioral Segmentation (Rule-Based RFM)
-- File: sql/11_customer_segmentation.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- SEGMENTATION LOGIC & BUSINESS RULES (No Black-Box ML):
-- Evaluated over the full 2025 platform observation period:
--
-- 1. Highly Engaged (Power Streamers):
--    - Total Watch Hours >= 30.0 AND Total Sessions >= 20
--    - Regular habit, multiple days per week, high content completion.
--
-- 2. Moderately Engaged (Casual Regulars):
--    - Total Watch Hours BETWEEN 10.0 AND 29.9 AND Total Sessions >= 8
--    - Consistent weekly or bi-weekly stream consumption.
--
-- 3. Low Engagement (Occasional / At-Risk):
--    - Total Watch Hours BETWEEN 1.0 AND 9.9 OR Sessions BETWEEN 1 AND 7
--    - Sporadic consumption, at high risk of disengagement.
--
-- 4. Inactive Users (Dormant / Ghost Signups):
--    - Total Watch Hours < 1.0 (or 0 sessions recorded)
--    - Signed up but never initiated substantial video playback.
-- ---------------------------------------------------------------------

CREATE OR REPLACE VIEW v_user_engagement_segments AS
WITH user_streaming_summary AS (
    SELECT
        u.user_id,
        u.signup_date,
        u.country,
        u.acquisition_channel,
        u.preferred_device,
        COUNT(vs.session_id) AS total_sessions,
        COALESCE(ROUND(SUM(vs.watch_minutes) / 60.0, 1), 0.0) AS total_watch_hours,
        COALESCE(ROUND(AVG(vs.completion_percentage), 2), 0.0) AS avg_completion_pct,
        MAX(vs.started_at) AS last_streamed_at
    FROM users u
    LEFT JOIN viewing_sessions vs ON u.user_id = vs.user_id
    GROUP BY u.user_id, u.signup_date, u.country, u.acquisition_channel, u.preferred_device
)
SELECT
    user_id,
    signup_date,
    country,
    acquisition_channel,
    preferred_device,
    total_sessions,
    total_watch_hours,
    avg_completion_pct,
    last_streamed_at,
    CASE
        WHEN total_watch_hours >= 30.0 AND total_sessions >= 20 THEN 'Highly Engaged'
        WHEN total_watch_hours >= 10.0 AND total_sessions >= 8  THEN 'Moderately Engaged'
        WHEN total_sessions >= 1                                THEN 'Low Engagement'
        ELSE 'Inactive'
    END AS engagement_segment
FROM user_streaming_summary;

-- ---------------------------------------------------------------------
-- QUERY G1: Segment Audience Breakdown & Streaming Metrics
-- ---------------------------------------------------------------------
SELECT
    engagement_segment,
    COUNT(user_id) AS total_users,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM users), 2) AS pct_of_audience,
    ROUND(AVG(total_sessions), 1) AS avg_sessions_per_user,
    ROUND(AVG(total_watch_hours), 1) AS avg_watch_hours_per_user,
    ROUND(AVG(avg_completion_pct), 2) AS avg_completion_percentage
FROM v_user_engagement_segments
GROUP BY engagement_segment
ORDER BY avg_watch_hours_per_user DESC;

-- ---------------------------------------------------------------------
-- QUERY G2: Segment vs Churn Behavior (The Retention Proof)
-- ---------------------------------------------------------------------
-- Business Question: What is the empirical relationship between engagement tier and subscription churn?
-- ---------------------------------------------------------------------
WITH user_subscription_status AS (
    SELECT
        user_id,
        MAX(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) AS has_active_sub,
        MAX(CASE WHEN status = 'Canceled' THEN 1 ELSE 0 END) AS has_canceled_sub
    FROM subscriptions
    GROUP BY user_id
)
SELECT
    ues.engagement_segment,
    COUNT(DISTINCT ues.user_id) AS total_users,
    COUNT(DISTINCT uss.user_id) AS paying_users,
    SUM(CASE WHEN uss.has_active_sub = 1 THEN 1 ELSE 0 END) AS currently_active_subscribers,
    SUM(CASE WHEN uss.has_active_sub = 0 AND uss.has_canceled_sub = 1 THEN 1 ELSE 0 END) AS churned_subscribers,
    ROUND(
        SUM(CASE WHEN uss.has_active_sub = 0 AND uss.has_canceled_sub = 1 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(COUNT(DISTINCT uss.user_id), 0),
        2
    ) AS segment_churn_rate_pct
FROM v_user_engagement_segments ues
LEFT JOIN user_subscription_status uss ON ues.user_id = uss.user_id
GROUP BY ues.engagement_segment
ORDER BY segment_churn_rate_pct ASC;

-- ---------------------------------------------------------------------
-- QUERY G3: Segment Distribution Across Acquisition Channels
-- ---------------------------------------------------------------------
-- Business Question: Which marketing channels are feeding our high-value segments vs creating inactive waste?
-- ---------------------------------------------------------------------
SELECT
    acquisition_channel,
    COUNT(user_id) AS channel_users,
    ROUND(SUM(CASE WHEN engagement_segment = 'Highly Engaged' THEN 1 ELSE 0 END) * 100.0 / COUNT(user_id), 1) AS pct_highly_engaged,
    ROUND(SUM(CASE WHEN engagement_segment = 'Moderately Engaged' THEN 1 ELSE 0 END) * 100.0 / COUNT(user_id), 1) AS pct_moderately_engaged,
    ROUND(SUM(CASE WHEN engagement_segment = 'Low Engagement' THEN 1 ELSE 0 END) * 100.0 / COUNT(user_id), 1) AS pct_low_engagement,
    ROUND(SUM(CASE WHEN engagement_segment = 'Inactive' THEN 1 ELSE 0 END) * 100.0 / COUNT(user_id), 1) AS pct_inactive
FROM v_user_engagement_segments
GROUP BY acquisition_channel
ORDER BY pct_highly_engaged DESC;
