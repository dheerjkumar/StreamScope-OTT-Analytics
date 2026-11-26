-- =====================================================================
-- StreamScope OTT Analytics
-- Script 03: Data Ingestion & Import Options
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- -------------------------------------------------------------
-- IMPORT OPTION A: LOAD DATA LOCAL INFILE (Fastest for Raw CSVs)
-- -------------------------------------------------------------
-- Note: Requires `local_infile = 1` enabled on client & server.
-- In MySQL Workbench: Edit Connection -> Advanced -> Others: OPT_LOCAL_INFILE=1
-- In MySQL CLI: mysql --local-infile=1 -u root -p streamscope

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Load Plans
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/plans.csv'
-- INTO TABLE plans
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (plan_id, plan_name, monthly_price, max_screens, video_quality);

-- 2. Load Content
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/content.csv'
-- INTO TABLE content
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (content_id, title, genre, release_year, content_type, duration_minutes);

-- 3. Load Users
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/users.csv'
-- INTO TABLE users
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (user_id, signup_date, country, age_group, acquisition_channel, preferred_device);

-- 4. Load Subscriptions
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/subscriptions.csv'
-- INTO TABLE subscriptions
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (subscription_id, user_id, plan_id, start_date, @end_date, status, billing_cycle, monthly_fee, @reason)
-- SET end_date = NULLIF(@end_date, ''), cancellation_reason = NULLIF(@reason, '');

-- 5. Load Viewing Sessions
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/viewing_sessions.csv'
-- INTO TABLE viewing_sessions
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (session_id, user_id, content_id, started_at, watch_minutes, completion_percentage, device_type);

-- 6. Load App Events
-- LOAD DATA LOCAL INFILE 'C:/Users/Dheeraj Kumar/OneDrive/Desktop/Documents/StreamScope-OTT-Analytics/data/raw/app_events.csv'
-- INTO TABLE app_events
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS
-- (event_id, user_id, event_timestamp, event_type, @content_id, device_type)
-- SET content_id = NULLIF(@content_id, '');

SET FOREIGN_KEY_CHECKS = 1;

-- -------------------------------------------------------------
-- IMPORT OPTION B: SEED SQL EXECUTION (Recommended & Most Compatible)
-- -------------------------------------------------------------
-- To avoid local_infile permissions, execute the pre-formatted seed script:
-- From PowerShell/Terminal:
--   mysql -u root -p streamscope < data/processed/streamscope_seed.sql
-- Or inside MySQL Workbench:
--   File -> Open SQL Script -> Select 'data/processed/streamscope_seed.sql' -> Execute (Lightning Bolt)

SELECT 'Review script comments for loading instructions.' AS notice;
