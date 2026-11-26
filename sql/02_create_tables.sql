-- =====================================================================
-- StreamScope OTT Analytics
-- Script 02: Table Schema Definition
-- Author: StreamScope Data & Product Analytics Team
-- RDBMS: MySQL 8.0+
-- =====================================================================

USE streamscope;

-- Disable foreign key checks during table drop/re-creation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS app_events;
DROP TABLE IF EXISTS viewing_sessions;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- -------------------------------------------------------------
-- Table 1: users
-- Core customer dimension table tracking signup demographics
-- -------------------------------------------------------------
CREATE TABLE users (
    user_id              INT PRIMARY KEY,
    signup_date          DATE NOT NULL,
    country              VARCHAR(50) NOT NULL,
    age_group            VARCHAR(20) NOT NULL,
    acquisition_channel  VARCHAR(50) NOT NULL,
    preferred_device     VARCHAR(30) NOT NULL,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_signup (signup_date),
    INDEX idx_users_channel (acquisition_channel),
    INDEX idx_users_country (country)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table 2: plans
-- Subscription plan tier specifications and pricing
-- -------------------------------------------------------------
CREATE TABLE plans (
    plan_id        INT PRIMARY KEY,
    plan_name      VARCHAR(50) NOT NULL UNIQUE,
    monthly_price  DECIMAL(6,2) NOT NULL,
    max_screens    INT NOT NULL,
    video_quality  VARCHAR(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table 3: subscriptions
-- Historical and ongoing paid subscriptions (allows multiple lifecycles)
-- -------------------------------------------------------------
CREATE TABLE subscriptions (
    subscription_id      INT PRIMARY KEY,
    user_id              INT NOT NULL,
    plan_id              INT NOT NULL,
    start_date           DATE NOT NULL,
    end_date             DATE NULL,
    status               ENUM('Active', 'Canceled', 'Expired') NOT NULL,
    billing_cycle        ENUM('Monthly', 'Annual') NOT NULL,
    monthly_fee          DECIMAL(6,2) NOT NULL,
    cancellation_reason  VARCHAR(100) NULL,
    CONSTRAINT fk_subscriptions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_subscriptions_plan FOREIGN KEY (plan_id) REFERENCES plans(plan_id),
    INDEX idx_subs_user_dates (user_id, start_date, end_date),
    INDEX idx_subs_status (status),
    INDEX idx_subs_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table 4: content
-- Catalogue of movies and web series with metadata
-- -------------------------------------------------------------
CREATE TABLE content (
    content_id        INT PRIMARY KEY,
    title             VARCHAR(100) NOT NULL,
    genre             VARCHAR(50) NOT NULL,
    release_year      INT NOT NULL,
    content_type      ENUM('Movie', 'Web Series') NOT NULL,
    duration_minutes  INT NOT NULL,
    INDEX idx_content_genre (genre),
    INDEX idx_content_type (content_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table 5: viewing_sessions
-- Fact table tracking video stream playback & consumption metrics
-- -------------------------------------------------------------
CREATE TABLE viewing_sessions (
    session_id             INT PRIMARY KEY,
    user_id                INT NOT NULL,
    content_id             INT NOT NULL,
    started_at             DATETIME NOT NULL,
    watch_minutes          INT NOT NULL,
    completion_percentage  DECIMAL(5,2) NOT NULL,
    device_type            VARCHAR(30) NOT NULL,
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_sessions_content FOREIGN KEY (content_id) REFERENCES content(content_id),
    INDEX idx_sessions_user_date (user_id, started_at),
    INDEX idx_sessions_content (content_id),
    INDEX idx_sessions_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -------------------------------------------------------------
-- Table 6: app_events
-- Clickstream behavioral interaction event log
-- -------------------------------------------------------------
CREATE TABLE app_events (
    event_id         INT PRIMARY KEY,
    user_id          INT NOT NULL,
    event_timestamp  DATETIME NOT NULL,
    event_type       VARCHAR(50) NOT NULL,
    content_id       INT NULL,
    device_type      VARCHAR(30) NOT NULL,
    CONSTRAINT fk_events_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_events_content FOREIGN KEY (content_id) REFERENCES content(content_id) ON DELETE SET NULL,
    INDEX idx_events_user_time (user_id, event_timestamp),
    INDEX idx_events_type (event_type),
    INDEX idx_events_timestamp (event_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'All 6 tables and indexes created successfully.' AS status;
