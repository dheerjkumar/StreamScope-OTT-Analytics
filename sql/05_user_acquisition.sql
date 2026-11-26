-- =====================================================================
-- StreamScope OTT Analytics
-- Module A: User Acquisition Analysis
-- File: sql/05_user_acquisition.sql
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- ---------------------------------------------------------------------
-- QUERY A1: Monthly User Registrations & Month-over-Month (MoM) Growth
-- ---------------------------------------------------------------------
-- Business Question: How is top-of-funnel user registration pacing month-by-month across 2025?
-- Why Needed: Evaluates marketing campaigns and seasonal sign-up velocity.
-- Tables: users
-- Functions: DATE_FORMAT, COUNT, LAG(), OVER(), ROUND
-- ---------------------------------------------------------------------
WITH monthly_signups AS (
    SELECT
        DATE_FORMAT(signup_date, '%Y-%m') AS signup_month,
        COUNT(user_id) AS new_registrations
    FROM users
    WHERE signup_date BETWEEN '2025-01-01' AND '2025-12-31'
    GROUP BY DATE_FORMAT(signup_date, '%Y-%m')
)
SELECT
    signup_month,
    new_registrations,
    LAG(new_registrations, 1) OVER (ORDER BY signup_month) AS prior_month_registrations,
    ROUND(
        (new_registrations - LAG(new_registrations, 1) OVER (ORDER BY signup_month)) 
        / LAG(new_registrations, 1) OVER (ORDER BY signup_month) * 100.0, 
        2
    ) AS mom_growth_pct,
    SUM(new_registrations) OVER (ORDER BY signup_month) AS cumulative_registrations
FROM monthly_signups
ORDER BY signup_month;

-- ---------------------------------------------------------------------
-- QUERY A2: Geographic Distribution of Registered Users
-- ---------------------------------------------------------------------
-- Business Question: What is the geographical breakdown of our audience base?
-- Why Needed: Guides localization, regional licensing, and multi-currency pricing strategy.
-- Tables: users
-- Functions: COUNT, SUM() OVER(), ROUND
-- ---------------------------------------------------------------------
SELECT
    country,
    COUNT(user_id) AS total_users,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM users), 2) AS pct_of_total_audience
FROM users
GROUP BY country
ORDER BY total_users DESC;

-- ---------------------------------------------------------------------
-- QUERY A3: Acquisition Channel Volume & Mix
-- ---------------------------------------------------------------------
-- Business Question: Which marketing channels are driving the highest volume of new accounts?
-- Why Needed: Informs marketing budget allocation across paid, organic, and referral channels.
-- Tables: users
-- Functions: COUNT, ROUND
-- ---------------------------------------------------------------------
SELECT
    acquisition_channel,
    COUNT(user_id) AS registered_users,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM users), 2) AS channel_share_pct
FROM users
GROUP BY acquisition_channel
ORDER BY registered_users DESC;

-- ---------------------------------------------------------------------
-- QUERY A4: Acquisition Channel to Paid Subscription Conversion Rate
-- ---------------------------------------------------------------------
-- Business Question: Which acquisition channels bring high-intent users who convert to paying subscribers vs casual free signups?
-- Why Needed: High registration volume means little if users do not convert to paying customers.
-- Tables: users, subscriptions
-- Joins: LEFT JOIN on user_id (to capture non-converting users)
-- Functions: COUNT(DISTINCT), ROUND, CASE WHEN
-- ---------------------------------------------------------------------
WITH user_first_sub AS (
    SELECT
        user_id,
        MIN(start_date) AS first_paid_date
    FROM subscriptions
    GROUP BY user_id
)
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS total_signups,
    COUNT(DISTINCT s.user_id) AS converted_subscribers,
    ROUND(COUNT(DISTINCT s.user_id) * 100.0 / COUNT(DISTINCT u.user_id), 2) AS conversion_rate_pct,
    ROUND(AVG(DATEDIFF(s.first_paid_date, u.signup_date)), 1) AS avg_days_to_convert
FROM users u
LEFT JOIN user_first_sub s ON u.user_id = s.user_id
GROUP BY u.acquisition_channel
ORDER BY conversion_rate_pct DESC;

-- ---------------------------------------------------------------------
-- QUERY A5: Age Group & Preferred Device Demographics
-- ---------------------------------------------------------------------
-- Business Question: How do user demographics correlate with preferred viewing hardware?
-- Why Needed: Helps engineering prioritize UI/UX optimization for Smart TVs vs Mobile apps.
-- Tables: users
-- Functions: COUNT, SUM(CASE WHEN ...)
-- ---------------------------------------------------------------------
SELECT
    age_group,
    COUNT(user_id) AS total_users,
    SUM(CASE WHEN preferred_device = 'Smart TV' THEN 1 ELSE 0 END) AS smart_tv_users,
    SUM(CASE WHEN preferred_device = 'Mobile' THEN 1 ELSE 0 END) AS mobile_users,
    SUM(CASE WHEN preferred_device = 'Laptop' THEN 1 ELSE 0 END) AS laptop_users,
    SUM(CASE WHEN preferred_device = 'Tablet' THEN 1 ELSE 0 END) AS tablet_users
FROM users
GROUP BY age_group
ORDER BY total_users DESC;
